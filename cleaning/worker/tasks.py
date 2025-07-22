import json
import requests
import shutil

from celery import Celery
from unstructured.partition.auto import partition
from bs4 import BeautifulSoup

from api.config import settings
from api.models import EntityToClean
from worker.utils import un_json


app = Celery('ckb', broker=settings.broker_url.unicode_string())


def clean_html(entity: EntityToClean):
    with entity.file_path.open('r') as f:
        soup = BeautifulSoup(f.read())

    return soup.get_text()


def clean_any_file(entity: EntityToClean):
    partitioned = partition(filename=entity.file_path.as_posix(), languages=settings.languages)
    cleaned_text = '\n\n'.join([str(el) for el in partitioned])
    return cleaned_text


@app.task
@un_json(EntityToClean)
def clean_file_task(entity: EntityToClean):
    with entity.meta_data_path.open('r') as f:
        metadata = json.load(f)

    if metadata['file_type'] == '.html':
        cleaned_text = clean_html(entity)
    else:
        cleaned_text = clean_any_file(entity)

    cleaned_text_filename = entity.directory_path / 'cleaned.txt'

    with cleaned_text_filename.open("w") as f:
        f.write(cleaned_text)

    r = requests.post(
        f"{settings.ruuter_internal}/ckb/pipeline/upload-file-sync",
        json={
            'source_file_path': cleaned_text_filename.as_posix(),
        }
    )
    uploaded_cleaned_text_url = r.json()['response']

    cleaned_metadata_filename = entity.directory_path / "cleaned.meta.json"
    with cleaned_metadata_filename.open("w") as f:
        metadata['metadata']['cleaned'] = True
        json.dump(metadata, f)

    r = requests.post(
        f"{settings.ruuter_internal}/ckb/pipeline/upload-file-sync",
        json={
            'source_file_path': cleaned_metadata_filename.as_posix(),
        }
    )
    uploaded_cleaned_metadata_url = r.json()['response']

    requests.post(
        f"{settings.ruuter_internal}/ckb/source-file/update-cleaned-file",
        json={
            'base_id': entity.source_file_id,
            'cleaned_data_url': uploaded_cleaned_text_url,
            'cleaned_metadata_url': uploaded_cleaned_metadata_url,
        }
    )

    shutil.rmtree(entity.directory_path)

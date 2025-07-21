import json

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

    cleaned_metadata_filename = entity.directory_path / "cleaned.meta.json"
    with cleaned_metadata_filename.open("w") as f:
        metadata['metadata']['cleaned'] = True
        json.dump(metadata, f)

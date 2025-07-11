import json

from celery import Celery
from unstructured.partition.auto import partition

from api.config import settings
from api.models import EntityToClean
from worker.utils import un_json


app = Celery('ckb', broker=settings.broker_url.unicode_string())


@app.task
@un_json(EntityToClean)
def clean_file_task(entity: EntityToClean):
    partitioned = partition(filename=entity.file_path.as_posix())
    cleaned_text = '\n\n'.join([str(el) for el in partitioned])

    cleaned_text_filename = entity.directory_path / 'cleaned.txt'

    with cleaned_text_filename.open("w") as f:
        f.write(cleaned_text)

    with entity.meta_data_path.open('r') as f:
        metadata = json.load(f)

    cleaned_metadata_filename = entity.directory_path / "cleaned.meta.json"
    with cleaned_metadata_filename.open("w") as f:
        metadata['metadata']['cleaned'] = True
        json.dump(metadata, f)

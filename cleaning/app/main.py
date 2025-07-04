import json

from fastapi import FastAPI

from app.models import EntityToClean
from app.config import settings

from unstructured.partition.auto import partition

app = FastAPI()


@app.post('/clean_file')
def clean_file(entity: EntityToClean):
    partitioned = partition(filename=entity.file_path.as_posix())
    cleaned_text = '\n\n'.join([str(el) for el in partitioned])
    cleaned_text_filename = settings.cleaned_data_path / (entity.file_path.name + ".cleaned.txt")
    with cleaned_text_filename.open("w") as f:
        f.write(cleaned_text)

    with entity.meta_data_path.open('r') as f:
        metadata = json.load(f)

    cleaned_metadata_filename = settings.cleaned_data_path / (entity.file_path.name + ".cleaned.txt.meta.json")
    with cleaned_metadata_filename.open("w") as f:
        metadata['metadata']['cleaned'] = True
        json.dump(metadata, f)

    return EntityToClean(
        file_path=cleaned_text_filename,
        meta_data_path=cleaned_metadata_filename
    )


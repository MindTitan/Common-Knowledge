from fastapi import FastAPI

from api.models import EntityToClean
from worker.tasks import clean_file_task


app = FastAPI()


@app.post('/clean_file')
def clean_file(entity: EntityToClean):
    clean_file_task.delay(entity.model_dump(mode='json'))

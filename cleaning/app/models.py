from pydantic import BaseModel, FilePath


class EntityToClean(BaseModel):
    file_path: FilePath
    meta_data_path: FilePath

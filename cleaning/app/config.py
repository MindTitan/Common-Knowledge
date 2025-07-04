from pydantic import DirectoryPath
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cleaned_data_path: DirectoryPath = '/cleaned-data'


settings = Settings()

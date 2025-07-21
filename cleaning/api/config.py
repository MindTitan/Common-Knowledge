from pydantic import AnyUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    broker_url: AnyUrl
    languages: list[str] = ['est', 'rus', 'eng']


settings = Settings()

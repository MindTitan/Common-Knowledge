from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, DirectoryPath


class Settings(BaseSettings):
    db_uri: PostgresDsn
    source_path: DirectoryPath = '/source'
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = 'us-east-1'
    s3_bucket_name: str
    s3_presigned_url_expiration: int = 3600


settings = Settings()

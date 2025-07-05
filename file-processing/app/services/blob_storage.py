from abc import ABC, abstractmethod
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from datetime import datetime, timedelta
from app.core.config import settings


class BlobStorageException(Exception):
    pass


class BlobStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, source_file_path: str, destination_path: str) -> str:
        pass

    @abstractmethod
    def generate_download_url(self, blob_path: str, expiration_seconds: int = 3600) -> str:
        pass

    @abstractmethod
    def file_exists(self, blob_path: str) -> bool:
        pass


class S3BlobStorageProvider(BlobStorageProvider):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name

    def upload_file(self, source_file_path: str, destination_path: str) -> str:
        try:
            if not os.path.exists(source_file_path):
                raise BlobStorageException(f"Source file not found: {source_file_path}")

            self.s3_client.upload_file(
                source_file_path,
                self.bucket_name,
                destination_path
            )
            return f"s3://{self.bucket_name}/{destination_path}"
        except NoCredentialsError:
            raise BlobStorageException("AWS credentials not found")
        except ClientError as e:
            raise BlobStorageException(f"S3 upload failed: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Upload failed: {str(e)}")

    def generate_download_url(self, blob_path: str, expiration_seconds: int = 3600) -> str:
        try:
            if not self.file_exists(blob_path):
                raise BlobStorageException(f"File not found in blob storage: {blob_path}")

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': blob_path
                },
                ExpiresIn=expiration_seconds
            )
            return url
        except NoCredentialsError:
            raise BlobStorageException("AWS credentials not found")
        except ClientError as e:
            raise BlobStorageException(f"Failed to generate download URL: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Failed to generate download URL: {str(e)}")

    def file_exists(self, blob_path: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=blob_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise BlobStorageException(f"Error checking file existence: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Error checking file existence: {str(e)}")


def get_blob_storage_provider() -> BlobStorageProvider:
    return S3BlobStorageProvider() 
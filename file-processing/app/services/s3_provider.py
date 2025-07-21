import boto3
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from app.services.blob_storage import BlobStorageProvider, BlobStorageException
from app.core.config import settings
import botocore.session

session = botocore.session.get_session()
session.set_config_variable('s3', {'signature_version': 's3v4'})

class S3Provider(BlobStorageProvider):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
            config=boto3.session.Config(signature_version='s3v4')
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

    def generate_download_url(self, path: str) -> tuple[str, datetime]:
        try:
            if not self.file_exists(path):
                raise BlobStorageException(f"File not found in blob storage: {path}")

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': path
                },
                ExpiresIn=settings.s3_presigned_url_expiration
            )
            expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=settings.s3_presigned_url_expiration)

            return url, expires_at
        except NoCredentialsError:
            raise BlobStorageException("AWS credentials not found")
        except ClientError as e:
            raise BlobStorageException(f"Failed to generate download URL: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Failed to generate download URL: {str(e)}")

    def file_exists(self, path: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise BlobStorageException(f"Error checking file existence: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Error checking file existence: {str(e)}")

    def download_file(self, s3_key: str, local_file_path: str) -> bool:
        """Download a file from S3 to local filesystem."""
        try:
            # Ensure the local directory exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Download the file
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                local_file_path
            )
            
            # Verify the file was downloaded
            if os.path.exists(local_file_path) and os.path.getsize(local_file_path) > 0:
                return True
            else:
                return False
                
        except NoCredentialsError:
            raise BlobStorageException("AWS credentials not found")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise BlobStorageException(f"File not found in S3: {s3_key}")
            else:
                raise BlobStorageException(f"S3 download failed: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Download failed: {str(e)}")

    def generate_upload_urls(self, paths: List[str], content_type: Optional[str] = None, expires_in: Optional[int] = None) -> List[tuple[str, str, datetime]]:
        """Generate presigned upload URLs for multiple blob paths."""
        try:
            expiration_seconds = expires_in or settings.s3_presigned_url_expiration
            expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=expiration_seconds)
            
            upload_urls = []
            
            for path in paths:
                # Clean the blob_path - remove any s3:// prefix if present
                clean_path = path
                if path.startswith('s3://'):
                    # Extract key from s3://bucket/key format
                    parts = path.replace('s3://', '').split('/', 1)
                    if len(parts) > 1:
                        clean_path = parts[1]
                    else:
                        clean_path = parts[0]
                
                params = {
                    'Bucket': self.bucket_name,
                    'Key': clean_path
                }
                
                # Add content type if provided
                if content_type:
                    params['ContentType'] = content_type
                
                url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params=params,
                    ExpiresIn=expiration_seconds
                )
                
                upload_urls.append((path, url, expires_at))
            
            return upload_urls
            
        except NoCredentialsError:
            raise BlobStorageException("AWS credentials not found")
        except ClientError as e:
            raise BlobStorageException(f"Failed to generate upload URLs: {str(e)}")
        except Exception as e:
            raise BlobStorageException(f"Failed to generate upload URLs: {str(e)}")


s3_provider = S3Provider()
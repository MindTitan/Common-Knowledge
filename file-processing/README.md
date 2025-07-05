# File Processing API

A FastAPI application for uploading files to blob storage with background task processing and download URL generation.

## Features

- File upload to S3 with background task processing
- Task status tracking in PostgreSQL
- Signed download URL generation
- Provider-agnostic blob storage interface

## Environment Variables

- `DB_URI`: PostgreSQL connection string (e.g., postgresql://user:pass@localhost/dbname)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)
- `S3_BUCKET_NAME`: S3 bucket name
- `S3_PRESIGNED_URL_EXPIRATION`: URL expiration time in seconds (default: 3600)
- `SOURCE_PATH`: Source directory path (default: /source)

## Database Setup

The application automatically creates the required `upload_tasks` table on startup with the following schema:

```sql
CREATE TABLE upload_tasks (
    task_id VARCHAR(36) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    source_file_path TEXT NOT NULL,
    blob_storage_path TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## API Endpoints

### POST /upload
Upload a file to blob storage.

**Request Body:**
```json
{
  "source_file_path": "path/to/file.txt"
}
```

**Response:**
```json
{
  "task_id": "uuid",
  "status": "pending"
}
```

### GET /tasks/{task_id}
Get the status of an upload task.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "completed",
  "source_file_path": "path/to/file.txt",
  "blob_storage_path": "s3://bucket/uploads/uuid/file.txt",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### POST /download
Generate a signed download URL for a file.

**Request Body:**
```json
{
  "blob_storage_path": "uploads/uuid/file.txt"
}
```

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/...",
  "expires_at": "2024-01-01T01:00:00"
}
```

## Running the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8888
```

Or using Docker:

```bash
docker build -t file-processing .
docker run -p 8888:8888 file-processing
```

Make sure to set the required environment variables, especially `DB_URI` for PostgreSQL connection. 
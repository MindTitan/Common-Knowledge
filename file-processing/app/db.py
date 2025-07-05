import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.config import settings


def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(settings.db_uri.unicode_string())


@contextmanager
def get_db_cursor():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    with get_db_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upload_tasks (
                task_id VARCHAR(36) PRIMARY KEY,
                status VARCHAR(20) NOT NULL,
                source_file_path TEXT NOT NULL,
                blob_storage_path TEXT,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """)
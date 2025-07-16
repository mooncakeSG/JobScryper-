import os
import sqlitecloud
from contextlib import contextmanager

SQLITE_CLOUD_URL = (
    f"sqlitecloud://{os.getenv('SQLITE_CLOUD_HOST')}:{os.getenv('SQLITE_CLOUD_PORT', '8860')}/"
    f"{os.getenv('SQLITE_CLOUD_DATABASE')}?apikey={os.getenv('SQLITE_CLOUD_API_KEY')}"
)

def get_connection():
    """Get a connection to SQLite Cloud."""
    return sqlitecloud.connect(SQLITE_CLOUD_URL)

@contextmanager
def cloud_db_connection():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def fetchall(query, params=None):
    with cloud_db_connection() as conn:
        cursor = conn.execute(query, params or ())
        return cursor.fetchall()

def fetchone(query, params=None):
    with cloud_db_connection() as conn:
        cursor = conn.execute(query, params or ())
        return cursor.fetchone()

def execute(query, params=None):
    with cloud_db_connection() as conn:
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor 
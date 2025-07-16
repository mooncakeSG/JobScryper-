import os
from dotenv import load_dotenv
import sqlitecloud

load_dotenv()

SQLITE_CLOUD_URL = (
    f"sqlitecloud://{os.getenv('SQLITE_CLOUD_HOST')}:{os.getenv('SQLITE_CLOUD_PORT', '8860')}/"
    f"{os.getenv('SQLITE_CLOUD_DATABASE')}?apikey={os.getenv('SQLITE_CLOUD_API_KEY')}"
)

def test_sqlitecloud_connection():
    print(f"Connecting to: {SQLITE_CLOUD_URL}")
    try:
        conn = sqlitecloud.connect(SQLITE_CLOUD_URL)
        result = conn.execute("SELECT 1").fetchone()
        print("Connection successful! Test query result:", result)
        conn.close()
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    test_sqlitecloud_connection() 
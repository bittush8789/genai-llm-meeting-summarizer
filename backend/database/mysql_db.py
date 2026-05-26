import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "meeting_summarizer")


def get_raw_connection():
    """Get a connection to MySQL server without selecting a database."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True
    )


def get_connection():
    """Get a connection to the specific meeting_summarizer database."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def init_db():
    """Create the database and tables if they do not exist."""
    # First connect without database to create it
    conn = get_raw_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    finally:
        conn.close()

    # Connect to the created database to create tables
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Create meetings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    transcript LONGTEXT,
                    summary TEXT,
                    decisions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Create action_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    meeting_id INT NOT NULL,
                    item TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("MySQL database and tables successfully initialized.")
    except Exception as e:
        print(f"Error initializing MySQL database: {e}")
        raise e
    finally:
        conn.close()


def save_meeting(title: str, transcript: str, summary: str, decisions: str, action_items: list) -> int:
    """
    Save meeting details and its associated action items in MySQL.
    Returns the meeting ID.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Insert into meetings
            cursor.execute(
                "INSERT INTO meetings (title, transcript, summary, decisions) VALUES (%s, %s, %s, %s)",
                (title, transcript, summary, decisions)
            )
            meeting_id = cursor.lastrowid

            # Insert action items
            for item in action_items:
                if item.strip():
                    cursor.execute(
                        "INSERT INTO action_items (meeting_id, item, status) VALUES (%s, %s, %s)",
                        (meeting_id, item.strip(), "pending")
                    )
            
            return meeting_id
    except Exception as e:
        print(f"Error saving meeting to MySQL: {e}")
        raise e
    finally:
        conn.close()

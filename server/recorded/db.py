import sqlite3
from pathlib import Path

DB_PATH = Path("recorded.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_cursor():
    conn = get_db_connection()
    return conn.cursor()


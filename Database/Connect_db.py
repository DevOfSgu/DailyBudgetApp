import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'finance_manager.db')

def get_db_connection():
    try:
        print(f"--- Đang kết nối tới database tại: {DATABASE_PATH} ---")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"LỖI KẾT NỐI DATABASE tại '{DATABASE_PATH}': {e}")
        return None
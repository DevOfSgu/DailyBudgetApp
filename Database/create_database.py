import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "finance_manager.db")

def create_database(db_path=DATABASE_PATH):

    try:
        # Kết nối tới cơ sở dữ liệu. File sẽ được tạo nếu chưa tồn tại.
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Cơ sở dữ liệu '{db_path}' đã được tạo hoặc kết nối thành công.")

        # --- Bảng người dùng ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # --- Bảng danh mục ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)

        # --- Bảng giao dịch ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            note TEXT,
            date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
        );
        """)

        # --- Bảng ngân sách ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            amount_limit REAL NOT NULL,
            month TEXT NOT NULL, -- định dạng: YYYY-MM
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
        );
        """)

        # --- Bảng mục tiêu tài chính ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline DATE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)

        # Lưu lại các thay đổi
        conn.commit()
        print("Tất cả các bảng đã được tạo thành công!")

    except sqlite3.Error as e:
        print(f"Lỗi khi tạo cơ sở dữ liệu: {e}")
    finally:
        # Đóng kết nối
        if conn:
            conn.close()
            print("Kết nối cơ sở dữ liệu đã được đóng.")

if __name__ == '__main__':
    create_database()
import sqlite3
import hashlib
from Database.Connect_db import get_db_connection

def get_user_by_username(username):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return user
    except sqlite3.Error as e:
        print(f"Lỗi database: {e}")
        return None
    finally:
        if conn:
            conn.close()
def check_user_exists(username, email):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
        user = cursor.fetchone()
        # Nếu tìm thấy người dùng (user không phải là None), trả về True. Ngược lại trả về False.
        return user is not None
    except sqlite3.Error as e:
        print(f"Lỗi database khi kiểm tra người dùng: {e}")
        # Mặc định trả về False nếu có lỗi để tránh các vấn đề khác
        return False
    finally:
        if conn:
            conn.close()

def create_user(user_data):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user_data['username'], user_data['email'], user_data['password_hash'])
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi database khi tạo người dùng: {e}")
        return False
    finally:
        if conn:
            conn.close()
def check_email_exist(email):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM users WHERE email = ?", (email,)
        )
        user = cursor.fetchone()
        return user is not None
    except sqlite3.Error as e:
        print(f"Lỗi database khi tạo người dùng: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_password_by_email(email, new_plain_password):
    new_password_hash = hashlib.sha256(new_plain_password.encode()).hexdigest()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE users SET password_hash = ? WHERE email = ?"
        cursor.execute(sql, (new_password_hash, email))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Đã cập nhật mật khẩu thành công cho email: {email}")
            return True
        else:
            print(f"Không tìm thấy người dùng có email {email} để cập nhật.")
            return False
    except sqlite3.Error as e:
        print(f"Lỗi database khi cập nhật mật khẩu: {e}")
        return False
    finally:
        if conn:
            conn.close()
def get_user_by_email(email):
    conn = None
    try:
        conn = get_db_connection()
        email_lower = email.strip().lower()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email_lower,))
        user = cursor.fetchone()
        return user
    except sqlite3.Error as e:
        print(f"Lỗi database khi lấy user bằng email: {e}")
        return None
    finally:
        if conn:
            conn.close()

def mark_user_as_old(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_new_user = 0 WHERE user_id = ? ",(user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Lỗi database khi lấy user bằng email: {e}")
        return None
    finally:
        if conn:
            conn.close()
def check_new_user(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT is_new_user
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = cursor.fetchone()
        count = result[0] if result else 0

        return count == 1
    except Exception as e:
        print(f"❌ [LOG ERROR] Không thể lấy log trước đó: {e}")
        return None
    finally:
        if conn:
            conn.close()



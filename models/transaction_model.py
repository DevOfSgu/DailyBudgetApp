import sqlite3
from Database.Connect_db import get_db_connection


def insert_transaction(data):
    conn = None
    note_raw = data.get('note')
    note = note_raw.strip() if isinstance(note_raw, str) else ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, category_id, amount, note, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['user_id'],
            data['type'],
            data['category_id'],
            data['amount'],
            note,
            data['date']
        ))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi database: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_or_create_category_id(user_id, name, trans_type):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Kiểm tra đã tồn tại
        cursor.execute("""
            SELECT category_id FROM categories
            WHERE user_id = ? AND name = ? AND type = ?
        """, (user_id, name.strip(), trans_type.strip()))
        result = cursor.fetchone()

        if result:
            return result[0]  # Đã có, trả về category_id

        # Nếu chưa có, tạo mới
        cursor.execute("""
            INSERT INTO categories (user_id, name, type)
            VALUES (?, ?, ?)
        """, (user_id, name.strip(), trans_type.strip()))
        conn.commit()
        return cursor.lastrowid

    except Exception as e:
        print(f"Lỗi khi lấy/tạo category: {e}")
        return None
    finally:
        if conn:
            conn.close()

def delete_transaction(transaction_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE transaction_id = ?",(transaction_id,))
        conn.commit()
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_oldest_transaction_date():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT MIN(date) FROM transactions""")
        result = cursor.fetchone()
        return result[0] if result and result[0] else None
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_transaction(data):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET amount = ?,
                type = ?,
                note = ?,
                date = ?,
                category_id = ?
            WHERE user_id = ? and transaction_id = ?;
        """,(data["amount"], data["type"], data["note"], data["date"], data["category_id"], data["user_id"], data["Transaction_id"]))
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()

def filter_transactions(filters):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """SELECT t.transaction_id, t.date, c.name, t.type, t.amount, t.note FROM transactions as t 
                    LEFT JOIN categories as c on t.category_id = c.category_id
                    WHERE t.user_id = ?
        """
        params = [filters["user_id"]]
        if filters.get("from_date") and filters.get("to_date"):
            query += """ AND substr(t.date, 7, 4) || '-' || substr(t.date, 4, 2) || '-' || substr(t.date, 1, 2)
    BETWEEN ? AND ? """
            params.extend([filters["from_date"], filters["to_date"]])
        if filters.get("category"):
            print(filters["category"])
            query += " AND c.name = ?"
            params.append(filters["category"])
        if filters.get("type"):
            print(filters["type"])
            query += " AND t.type = ?"
            params.append(filters["type"])

        if filters.get("min_price"):
            query += " AND amount >= ?"
            params.append(float(filters["min_price"]))

        if filters.get("max_price"):
            query += " AND amount <= ?"
            params.append(float(filters["max_price"]))
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()

def transaction_data(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT transaction_id, date, C.name, T.type, amount, note FROM transactions AS T
                                    JOIN categories AS C ON C.category_id = T.category_id
                                    WHERE T.user_id = ?
        """,(user_id,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_balance(data):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM month_balance
                WHERE user_id = ? AND month = ? AND year = ?
            """, (data["user_id"], data["month"], data["year"]))
        exists = cursor.fetchone()[0]

        if exists:
                cursor.execute("""
                     UPDATE month_balance
                     SET initial_balance = ?
                     WHERE user_id = ? AND month = ? AND year = ?
                """, (data["balance"], data["user_id"], data["month"], data["year"]))
        else:
                 cursor.execute("""
                         INSERT INTO month_balance (user_id, month, year, initial_balance)
                         VALUES (?, ?, ?, ?)
                """, (data["user_id"], data["month"], data["year"], data["balance"]))

        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        if conn:
            conn.close()
import sqlite3
from Database.Connect_db import get_db_connection

def get_income(user_id, month,year):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, SUM(amount) AS Sum_amount
            FROM transactions
            WHERE user_id = ?
              AND substr(date, 4, 2) = ?
              AND type = ?
              AND substr(date, 7, 4) = ?
        """, (str(user_id), str(month).zfill(2), 'income',str(year)))
        result = cursor.fetchone()
        if result and result[1] is not None:
            value = result[1]
        else:
            value = 0
        return value
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_expense(user_id, month,year):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, SUM(amount) AS Sum_amount
            FROM transactions
            WHERE user_id = ?
              AND substr(date, 4, 2) = ?
              AND type = ?
              AND substr(date, 7, 4) = ?
        """, (str(user_id), str(month).zfill(2), 'expense', str(year)))
        result = cursor.fetchone()
        if result and result[1] is not None:
            value = result[1]
        else:
            value = 0
        return value
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        if conn:
            conn.close()
def get_balance(userid,month,year):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT initial_balance 
            FROM month_balance
            WHERE user_id = ? and month = ? and year = ?;
        """,(userid,month,year))
        result = cursor.fetchone()
        if result and result[0] is not None:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"Lỗi: {e}")
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

def get_top_5_transaction(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, C.name, T.type, amount
            FROM transactions AS T
            JOIN categories AS C ON C.category_id = T.category_id
            WHERE T.user_id = ?
            ORDER BY 
            SUBSTR(date, 7, 4) || '-' || SUBSTR(date, 4, 2) || '-' || SUBSTR(date, 1, 2) || ' ' || SUBSTR(date, 12)
            DESC
            LIMIT 5;
        """,(user_id,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_income_each_month(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT substr(date, 4, 2) AS month, SUM(amount) AS total_amount
            FROM transactions
            WHERE type = 'income' 
            AND user_id = ?
            AND substr(date, 7, 4) = strftime('%Y', 'now') 
            GROUP BY month
            ORDER BY month;
        """,(user_id,))
        results = cursor.fetchall()
        return {row[0]: row[1] for row in results}
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_expense_each_month(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT substr(date, 4, 2) AS month, SUM(amount) AS total_amount
            FROM transactions
            WHERE type = 'expense' 
            AND user_id = ?
            AND substr(date, 7, 4) = strftime('%Y', 'now') 
            GROUP BY month
            ORDER BY month;
        """,(user_id,))
        results = cursor.fetchall()
        return {row[0]: row[1] for row in results}
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_data_of_expense(user_id, month):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name, sum(t.amount) as total_amount
            FROM transactions as t 
            JOIN categories as c ON t.category_id = c.category_id
            WHERE t.type = "expense" AND t.user_id = ?
            AND CAST(substr(t.date, 4, 2) AS INTEGER) = ?
            GROUP BY c.name
            ORDER BY total_amount DESC
        """,(user_id, month,))
        results = cursor.fetchall()
        return {row[0]: row[1] for row in results}
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        if conn:
            conn.close()
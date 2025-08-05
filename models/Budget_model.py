import sqlite3
from datetime import date

from Database.Connect_db import get_db_connection

def insert_budget(data):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO budgets (user_id, category_id, amount_limit, month, year, week)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['user_id'],
            data['category_id'],
            data['amount_limit'],
            data['month'],
            data['year'],
            data['week']
        ))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi database: {e}")
        return False
    finally:
        if conn:
            conn.close()

def budget_data(user_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today()
        year = str(today.year)
        month = f"{today.month:02d}"
        week = today.isocalendar()[1]

        cursor.execute("""
            SELECT 
                b.budget_id,
                c.name AS category_name,
                b.amount_limit,
                IFNULL(SUM(t.amount), 0) AS spent,
                b.amount_limit - IFNULL(SUM(t.amount), 0) AS remaining,
                b.week,
                b.month,
                b.year
            FROM budgets AS b
            JOIN categories AS c ON c.category_id = b.category_id
            LEFT JOIN transactions AS t 
                ON t.category_id = b.category_id 
                AND t.type = 'expense'
                AND (
                    (b.week IS NOT NULL 
                        AND substr(t.date, 7, 4) = ? 
                        AND substr(t.date, 4, 2) = ? 
                        AND CAST(strftime('%W', DATE(substr(t.date, 7, 4) || '-' || substr(t.date, 4, 2) || '-' || substr(t.date, 1, 2))) AS INTEGER) = ?

                    )
                    OR
                    (b.week IS NULL 
                        AND b.month IS NOT NULL 
                        AND substr(t.date, 7, 4) = ? 
                        AND substr(t.date, 4, 2) = ?
                    )
                    OR
                    (b.week IS NULL 
                        AND b.month IS NULL 
                        AND substr(t.date, 7, 4) = ?
                    )
                )
            WHERE b.user_id = ?
            GROUP BY b.budget_id
        """, (
            year, month, week,  # cho tuần
            year, month,        # cho tháng
            year,               # cho năm
            user_id             # người dùng
        ))

        raw_rows = cursor.fetchall()
        processed_rows = []

        for row in raw_rows:
            budget_id, category, limit, spent, remaining, w, m, y = row
            if w is not None:
                period = "week"
            elif m is not None:
                period = "month"
            elif y is not None:
                period = "year"
            else:
                period = "unknown"
            processed_rows.append((budget_id, category, limit, spent, remaining, period))

        return processed_rows

    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        if conn:
            conn.close()

def delete_budget(budget_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE budget_id = ?",(budget_id,))
        conn.commit()
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_budget(data):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE budgets
            SET category_id = ?,
                amount_limit = ?,
                month = ?,
                year = ?,
                week = ?
            WHERE user_id = ? AND budget_id = ?;
        """, (
            data["category_id"],
            data["amount"],
            data["month"],
            data["year"],
            data["week"],
            data["user_id"],
            data["budget_id"]
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi : {e}")
        return None
    finally:
        if conn:
            conn.close()


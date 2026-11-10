
import sqlite3
import os

DATABASE_PATH = os.path.join("instance", "finance.db")


def get_connection():
    os.makedirs("instance", exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_transaction(title, amount, transaction_type, category, date):
    conn = get_connection()

    conn.execute("""
        INSERT INTO transactions
        (title, amount, transaction_type, category, date)
        VALUES (?, ?, ?, ?, ?)
    """, (title, amount, transaction_type, category, date))

    conn.commit()
    conn.close()


def get_transactions():
    conn = get_connection()

    transactions = conn.execute("""
        SELECT * FROM transactions
        ORDER BY date DESC, id DESC
    """).fetchall()

    conn.close()
    return [dict(row) for row in transactions]


def delete_transaction(transaction_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    conn.commit()
    conn.close()


def get_summary():
    conn = get_connection()

    income = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'income'
    """).fetchone()[0]

    expenses = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE transaction_type = 'expense'
    """).fetchone()[0]

    conn.close()

    return {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses
    }


if __name__ == "__main__":
    init_db()
    print("Database created successfully!")

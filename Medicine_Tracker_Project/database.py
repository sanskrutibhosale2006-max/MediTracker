import sqlite3

def connect_db():

    conn = sqlite3.connect('medicine.db')

    conn.row_factory = sqlite3.Row

    return conn


def create_table():

    conn = connect_db()

    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute('''

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )

    ''')

    # MEDICINES TABLE
    cursor.execute('''

        CREATE TABLE IF NOT EXISTS medicines (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT,

            supplier TEXT,

            stock INTEGER NOT NULL,

            expiry TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

    ''')

    conn.commit()

    conn.close()
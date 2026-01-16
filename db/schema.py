# file: db/schema.py
import sqlite3

DB_NAME = "car_rental.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            plate TEXT UNIQUE NOT NULL,
            daily_price REAL NOT NULL CHECK (daily_price > 0),
            available INTEGER NOT NULL CHECK (available IN (0, 1))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            renter TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            FOREIGN KEY (car_id)
                REFERENCES cars (id)
                ON DELETE CASCADE
        )
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_rentals_car_id ON rentals(car_id)"
    )

    conn.commit()
    conn.close()

# file: db/repository.py
import sqlite3
from db.schema import DB_NAME


class CarRepository:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row

    # ---------- ADMIN ----------
    def add_car(self, model, plate, daily_price):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO cars (model, plate, daily_price, available)
            VALUES (?, ?, ?, 1)
            """,
            (model, plate, daily_price),
        )
        self.conn.commit()

    def delete_car(self, car_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM cars WHERE id = ?", (car_id,))
        self.conn.commit()

    def update_car(self, car_id, model, price, renter, pickup, return_):
        cur = self.conn.cursor()

        # Update car info
        cur.execute(
            "UPDATE cars SET model = ?, daily_price = ? WHERE id = ?",
            (model, price, car_id),
        )

        # Remove existing rental
        cur.execute("DELETE FROM rentals WHERE car_id = ?", (car_id,))

        # If rental info exists, insert again
        if renter and pickup and return_:
            cur.execute(
                """
                INSERT INTO rentals (car_id, renter, pickup_date, return_date)
                VALUES (?, ?, ?, ?)
                """,
                (car_id, renter, pickup, return_),
            )
            cur.execute(
                "UPDATE cars SET available = 0 WHERE id = ?",
                (car_id,),
            )
        else:
            cur.execute(
                "UPDATE cars SET available = 1 WHERE id = ?",
                (car_id,),
            )

        self.conn.commit()

    # ---------- QUERIES ----------
    def get_car(self, car_id):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT
                c.id, c.model, c.plate, c.daily_price, c.available,
                r.renter, r.pickup_date, r.return_date
            FROM cars c
            LEFT JOIN rentals r
                ON c.id = r.car_id
            WHERE c.id = ?
            """,
            (car_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Car not found")
        return dict(row)

    def list_cars_detailed(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT
                c.id, c.model, c.plate, c.daily_price, c.available,
                r.renter, r.pickup_date, r.return_date
            FROM cars c
            LEFT JOIN rentals r
                ON c.id = r.car_id
            ORDER BY c.id
            """
        )
        return [dict(row) for row in cur.fetchall()]

    # ---------- RENTAL ----------
    def mark_rented(self, car_id, renter, pickup_date, return_date):
        cur = self.conn.cursor()

        cur.execute(
            "UPDATE cars SET available = 0 WHERE id = ? AND available = 1",
            (car_id,),
        )
        if cur.rowcount == 0:
            raise ValueError("Car not available")

        cur.execute(
            """
            INSERT INTO rentals (car_id, renter, pickup_date, return_date)
            VALUES (?, ?, ?, ?)
            """,
            (car_id, renter, pickup_date, return_date),
        )

        self.conn.commit()

    def mark_returned(self, car_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM rentals WHERE car_id = ?", (car_id,))
        cur.execute("UPDATE cars SET available = 1 WHERE id = ?", (car_id,))
        self.conn.commit()

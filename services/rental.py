# file: services/rental.py
from datetime import date
from db.repository import CarRepository


class RentalService:
    def __init__(self):
        self.repo = CarRepository()

    def add_car(self, model, plate, price):
        if not model or not plate:
            raise ValueError("Model and plate required")
        if price <= 0:
            raise ValueError("Invalid price")
        self.repo.add_car(model, plate, price)

    def list_cars(self):
        return self.repo.list_cars_detailed()

    def rent_car(self, car_id, renter, pickup, return_):
        if pickup >= return_:
            raise ValueError("Invalid rental dates")

        car = self.repo.get_car(car_id)
        if not car["available"]:
            raise ValueError("Car already rented")

        self.repo.mark_rented(
            car_id,
            renter,
            pickup.isoformat(),
            return_.isoformat(),
        )

    def calculate_total(self, car):
        if car["available"]:
            return None, None

        pickup = date.fromisoformat(car["pickup_date"])
        return_ = date.fromisoformat(car["return_date"])

        days = (return_ - pickup).days
        total = days * car["daily_price"]
        return days, total

    def return_car(self, car_id):
        self.repo.mark_returned(car_id)

    def delete_car(self, car_id):
        self.repo.delete_car(car_id)

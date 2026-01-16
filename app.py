# file: app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db.schema import init_db
from services.rental import RentalService


# ---------------- RENT DIALOG ----------------
class RentDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Rent Car")
        self.result = None

        ttk.Label(self, text="Customer Name").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self, text="Pickup Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(self, text="Return Date (YYYY-MM-DD)").grid(row=2, column=0, padx=5, pady=5)

        self.name_entry = ttk.Entry(self)
        self.pickup_entry = ttk.Entry(self)
        self.return_entry = ttk.Entry(self)

        self.name_entry.grid(row=0, column=1)
        self.pickup_entry.grid(row=1, column=1)
        self.return_entry.grid(row=2, column=1)

        ttk.Button(self, text="Confirm", command=self.confirm).grid(row=3, column=0, pady=10)
        ttk.Button(self, text="Cancel", command=self.destroy).grid(row=3, column=1, pady=10)

        self.grab_set()
        self.wait_window()

    def confirm(self):
        self.result = (
            self.name_entry.get(),
            self.pickup_entry.get(),
            self.return_entry.get(),
        )
        self.destroy()


# ---------------- EDIT DIALOG ----------------
class EditDialog(tk.Toplevel):
    def __init__(self, parent, car):
        super().__init__(parent)
        self.title("Edit Car / Rental")
        self.result = None

        labels = ["Model", "Daily Price", "Renter", "Pickup Date", "Return Date"]
        for i, text in enumerate(labels):
            ttk.Label(self, text=text).grid(row=i, column=0, padx=5, pady=5)

        self.model = ttk.Entry(self)
        self.price = ttk.Entry(self)
        self.renter = ttk.Entry(self)
        self.pickup = ttk.Entry(self)
        self.return_ = ttk.Entry(self)

        self.model.insert(0, car["model"])
        self.price.insert(0, car["daily_price"])
        self.renter.insert(0, car.get("renter", "") or "")
        self.pickup.insert(0, car.get("pickup_date", "") or "")
        self.return_.insert(0, car.get("return_date", "") or "")

        self.model.grid(row=0, column=1)
        self.price.grid(row=1, column=1)
        self.renter.grid(row=2, column=1)
        self.pickup.grid(row=3, column=1)
        self.return_.grid(row=4, column=1)

        ttk.Button(self, text="Save", command=self.save).grid(row=5, column=0, pady=10)
        ttk.Button(self, text="Cancel", command=self.destroy).grid(row=5, column=1)

        self.grab_set()
        self.wait_window()

    def save(self):
        self.result = {
            "model": self.model.get(),
            "price": float(self.price.get()),
            "renter": self.renter.get(),
            "pickup": self.pickup.get(),
            "return": self.return_.get(),
        }
        self.destroy()


# ---------------- MAIN APP ----------------
class CarRentalApp:
    def __init__(self, root):
        init_db()
        self.service = RentalService()

        self.root = root
        self.root.title("Car Rental System")
        self.root.geometry("900x500")

        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        ttk.Label(self.root, text="Car Rental System",
                  font=("Arial", 16, "bold")).pack(pady=10)

        form = ttk.LabelFrame(self.root, text="Add Car (Admin)")
        form.pack(fill="x", padx=10)

        ttk.Label(form, text="Model").grid(row=0, column=0)
        ttk.Label(form, text="Plate").grid(row=0, column=2)
        ttk.Label(form, text="Daily Price").grid(row=0, column=4)

        self.model_entry = ttk.Entry(form)
        self.plate_entry = ttk.Entry(form)
        self.price_entry = ttk.Entry(form)

        self.model_entry.grid(row=0, column=1)
        self.plate_entry.grid(row=0, column=3)
        self.price_entry.grid(row=0, column=5)

        ttk.Button(form, text="Add Car",
                   command=self.add_car).grid(row=0, column=6, padx=5)

        self.table = ttk.Treeview(
            self.root,
            columns=("ID", "Model", "Plate", "Price", "Status", "Days", "Total"),
            show="headings",
        )

        for col in self.table["columns"]:
            self.table.heading(col, text=col)

        # FIXED WIDTHS (NO HORIZONTAL SCROLL)
        self.table.column("ID", width=40, anchor="center")
        self.table.column("Model", width=120)
        self.table.column("Plate", width=90)
        self.table.column("Price", width=70, anchor="e")
        self.table.column("Status", width=80, anchor="center")
        self.table.column("Days", width=50, anchor="center")
        self.table.column("Total", width=70, anchor="e")

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        buttons = ttk.Frame(self.root)
        buttons.pack(pady=5)

        ttk.Button(buttons, text="Rent", command=self.rent_car).pack(side="left", padx=5)
        ttk.Button(buttons, text="Edit", command=self.edit_car).pack(side="left", padx=5)
        ttk.Button(buttons, text="Return", command=self.return_car).pack(side="left", padx=5)
        ttk.Button(buttons, text="Delete", command=self.delete_car).pack(side="left", padx=5)

    def refresh_table(self):
        self.table.delete(*self.table.get_children())

        for car in self.service.list_cars():
            days, total = self.service.calculate_total(car)

            self.table.insert(
                "",
                "end",
                values=(
                    car["id"],
                    car["model"],
                    car["plate"],
                    car["daily_price"],
                    "Available" if car["available"] else "Rented",
                    days if days else "-",
                    total if total else "-",
                ),
            )

    def get_selected_car_id(self):
        selected = self.table.selection()
        if not selected:
            raise ValueError("Please select a car")
        return int(self.table.item(selected[0])["values"][0])

    def add_car(self):
        try:
            self.service.add_car(
                self.model_entry.get(),
                self.plate_entry.get(),
                float(self.price_entry.get()),
            )
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def rent_car(self):
        try:
            car_id = self.get_selected_car_id()
            dialog = RentDialog(self.root)
            if not dialog.result:
                return

            name, pickup, return_ = dialog.result
            pickup_date = datetime.strptime(pickup, "%Y-%m-%d").date()
            return_date = datetime.strptime(return_, "%Y-%m-%d").date()

            self.service.rent_car(car_id, name, pickup_date, return_date)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_car(self):
        try:
            car_id = self.get_selected_car_id()
            car = self.service.repo.get_car(car_id)

            dialog = EditDialog(self.root, car)
            if not dialog.result:
                return

            self.service.repo.update_car(
                car_id,
                dialog.result["model"],
                dialog.result["price"],
                dialog.result["renter"],
                dialog.result["pickup"],
                dialog.result["return"],
            )

            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_car(self):
        try:
            self.service.return_car(self.get_selected_car_id())
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_car(self):
        try:
            self.service.delete_car(self.get_selected_car_id())
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    CarRentalApp(root)
    root.mainloop()

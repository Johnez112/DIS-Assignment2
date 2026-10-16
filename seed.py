"""Creates the three SQLite databases and fills them with dummy data.

Run:  python seed.py
Running it again resets all databases to the original dummy data.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "databases")

CUSTOMERS = [
    ("Matti Virtanen", "040 123 4567", "matti.virtanen@example.com", "Koulukatu 12", "Lappeenranta"),
    ("Anna Korhonen", "050 234 5678", "anna.korhonen@example.com", "Rantatie 4", "Imatra"),
    ("Taloyhtiö As Oy Kanava", "05 456 7890", "isannoitsija@kanava.example.com", "Kanavatie 20", "Lappeenranta"),
    ("Juha Nieminen", "044 345 6789", "juha.nieminen@example.com", "Mäntytie 7", "Joensuu"),
    ("Liisa Mäkinen", "045 456 7891", "liisa.makinen@example.com", "Peltokatu 3 B 9", "Lappeenranta"),
    ("Rakennus Oy Saimaa", "05 678 9012", "tilaukset@saimaa.example.com", "Teollisuuskatu 15", "Savonlinna"),
]

PROJECTS = [
    (1, "House exterior repaint", "Exterior", 180, 6400, "Completed", "2026-06-01"),
    (2, "Living room and kitchen walls", "Interior", 65, 1450, "Completed", "2026-08-12"),
    (3, "Stairwell painting, 3 floors", "Interior", 240, 5200, "In progress", "2026-10-05"),
    (4, "Wooden fence and terrace", "Exterior", 45, 900, "Planned", "2027-05-15"),
    (5, "Bedroom wallpaper removal and painting", "Interior", 30, 780, "Offer sent", "2026-11-02"),
    (6, "Office building facade", "Exterior", 620, 18500, "Offer sent", "2027-04-20"),
    (1, "Garage door and trim", "Exterior", 20, 450, "Planned", "2027-05-02"),
]

PAINTS = [
    ("Tikkurila", "Harmony", "Interior wall paint", "F497 white", 90.0, 14.50),
    ("Tikkurila", "Valtti Color", "Wood stain", "5065 grey", 36.0, 18.90),
    ("Tikkurila", "Pika-Teho", "Exterior house paint", "Y374 red", 54.0, 16.20),
    ("Teknos", "Biora Air", "Interior wall paint", "T1500 white", 40.0, 13.80),
    ("Teknos", "Woodex Aqua", "Wood oil", "Clear", 18.0, 21.40),
    ("Tikkurila", "Otex", "Primer", "White", 27.0, 15.60),
    ("Teknos", "Futura Aqua 40", "Metal / trim paint", "Black", 6.0, 24.90),
]


def create_db(filename, schema, insert_sql, rows):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    con.execute(schema)
    con.executemany(insert_sql, rows)
    con.commit()
    con.close()
    print(f"Created {filename} ({len(rows)} rows)")


def seed():
    os.makedirs(DB_DIR, exist_ok=True)

    create_db(
        "customers.db",
        """CREATE TABLE customers (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               phone TEXT,
               email TEXT,
               address TEXT,
               city TEXT
           )""",
        "INSERT INTO customers (name, phone, email, address, city) VALUES (?, ?, ?, ?, ?)",
        CUSTOMERS,
    )

    create_db(
        "projects.db",
        """CREATE TABLE projects (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               customer_id INTEGER,
               description TEXT NOT NULL,
               job_type TEXT,
               area_m2 REAL,
               price_eur REAL,
               status TEXT,
               start_date TEXT
           )""",
        "INSERT INTO projects (customer_id, description, job_type, area_m2, price_eur, status, start_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        PROJECTS,
    )

    create_db(
        "inventory.db",
        """CREATE TABLE paints (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               brand TEXT,
               product TEXT NOT NULL,
               paint_type TEXT,
               colour TEXT,
               litres_in_stock REAL,
               price_per_litre_eur REAL
           )""",
        "INSERT INTO paints (brand, product, paint_type, colour, litres_in_stock, price_per_litre_eur) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        PAINTS,
    )


if __name__ == "__main__":
    seed()

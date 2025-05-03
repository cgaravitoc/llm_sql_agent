import sqlite3
import random
from faker import Faker
import os

# Path to SQLite DB
sql_db_path = os.path.join(os.getcwd(), "data", "sales_dimensional.db")

# Create faker instance
faker = Faker()

# Connect to SQLite DB
conn = sqlite3.connect(sql_db_path)
cursor = conn.cursor()

# Drop tables if they exist
cursor.execute("DROP TABLE IF EXISTS sales")
cursor.execute("DROP TABLE IF EXISTS clientes")
cursor.execute("DROP TABLE IF EXISTS stores")

# Create tables
cursor.execute("""
    CREATE TABLE clientes (
        client_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        country TEXT
    )
""")

cursor.execute("""
    CREATE TABLE stores (
        store_id INTEGER PRIMARY KEY,
        name TEXT,
        city TEXT,
        country TEXT
    )
""")

cursor.execute("""
    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY,
        client_id INTEGER,
        store_id INTEGER,
        sale_date TEXT,
        amount REAL,
        FOREIGN KEY(client_id) REFERENCES clientes(client_id),
        FOREIGN KEY(store_id) REFERENCES stores(store_id)
    )
""")

# Insert 100 clients
for i in range(100):
    cursor.execute("""
        INSERT INTO clientes (name, email, country)
        VALUES (?, ?, ?)
    """, (faker.name(), faker.email(), faker.country()))

# Insert 100 stores
for i in range(100):
    cursor.execute("""
        INSERT INTO stores (name, city, country)
        VALUES (?, ?, ?)
    """, (faker.company(), faker.city(), faker.country()))

# Insert 100 sales with random client and store references
for i in range(100):
    cursor.execute("""
        INSERT INTO sales (client_id, store_id, sale_date, amount)
        VALUES (?, ?, ?, ?)
    """, (
        random.randint(1, 100),  # client_id
        random.randint(1, 100),  # store_id
        faker.date_this_decade().isoformat(),  # sale_date
        round(random.uniform(10.0, 1000.0), 2)  # amount
    ))

# Commit and close
conn.commit()
conn.close()

print("Database 'sales_dimensional.db' created with 3 tables and 100 records each.")

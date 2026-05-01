import os
import sqlite3

os.makedirs('transactions', exist_ok=True)
conn = sqlite3.connect('transactions/transactions.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER,
    commodity TEXT,
    quantity REAL,
    price REAL,
    total REAL
)
''')
conn.commit()
conn.close()
print('transactions/transactions.db created and initialized')

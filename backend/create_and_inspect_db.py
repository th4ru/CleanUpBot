#!/usr/bin/env python3
"""
Create DB tables and inspect SQLite DB for CleanUpBot backend.
"""
from app import create_app
from models import db
import sqlite3, os, sys

app = create_app()
with app.app_context():
    db.create_all()
    print('created tables')

# DB path relative to this file
db_path = os.path.join(os.path.dirname(__file__), 'system_manager.db')
print('DB path:', db_path)
if not os.path.exists(db_path):
    print('DB not found at', db_path)
    sys.exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('--- tables ---')
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"):
    print(row[0])

print('--- schema system_pcs ---')
try:
    for row in cur.execute("PRAGMA table_info('system_pcs');"):
        print(row)
except Exception as e:
    print('schema error:', e)

print('--- sample rows (up to 10) ---')
try:
    for row in cur.execute("SELECT id, pc_name, ip_address, username, status, last_seen FROM system_pcs LIMIT 10;"):
        print(row)
except Exception as e:
    print('query error:', e)

conn.close()

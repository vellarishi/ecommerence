"""
Reads live restaurant/menu data straight out of ruchi.db (the same SQLite
file backend/app.py writes to), so the chatbot's answers about "what
restaurants are available" always match what's actually in the database
instead of a hardcoded list that goes stale the moment admin adds a product.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "instance" / "ruchi.db"


def get_active_products() -> list:
    """Returns every active product row as a plain dict. Returns [] if the
    db file doesn't exist yet (e.g. backend has never been run) instead of
    raising, so the chatbot still works with just the static FAQ entries."""
    if not DB_PATH.exists():
        return []

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """SELECT name, cuisine, price_value, rating, delivery_time, description
               FROM products WHERE is_active = 1 ORDER BY id"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        con.close()

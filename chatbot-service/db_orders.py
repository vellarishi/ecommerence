"""
Reads a logged-in customer's own order history straight out of ruchi.db,
keyed by their auth token (the same bearer token login.html/cart.html
store in localStorage), so the LLM chatbot can answer real questions like
"how many orders have I placed?" or "what's my last order status?" with
actual data instead of guessing from the static FAQ.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "instance" / "ruchi.db"


def get_orders_for_token(token: str) -> list:
    """Returns this customer's orders (newest first) as plain dicts, or []
    if the token doesn't match anyone / the db isn't there yet."""
    if not token or not DB_PATH.exists():
        return []

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        customer = con.execute(
            "SELECT id FROM customers WHERE auth_token = ?", (token,)
        ).fetchone()
        if not customer:
            return []

        orders = con.execute(
            """SELECT id, status, subtotal, delivery_fee, tax, discount, total, created_at
               FROM orders WHERE customer_id = ? ORDER BY created_at DESC""",
            (customer["id"],),
        ).fetchall()

        result = []
        for order in orders:
            items = con.execute(
                """SELECT product_name, quantity, price_value FROM order_items
                   WHERE order_id = ?""",
                (order["id"],),
            ).fetchall()
            order_dict = dict(order)
            order_dict["items"] = [dict(item) for item in items]
            result.append(order_dict)
        return result
    finally:
        con.close()

# Ruchi Backend (Flask + SQLite)

This turns your static Ruchi site into a dynamic one:
- **Products** are now stored in a real database — editable from an admin panel instead of hardcoded in `script.js`.
- **Orders** are saved when a customer checks out, and can be tracked / updated from the admin panel.

## 1. Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs at **http://127.0.0.1:5000**

First run automatically:
- Creates the SQLite database at `instance/ruchi.db`
- Creates a default admin login → **username: `admin`  password: `ruchi123`**
- Seeds your 4 existing dummy restaurants as real products

**Change the default admin password** by setting an environment variable before first run:
```bash
export ADMIN_PASSWORD="your-new-password"
```

## 2. Admin Panel

Open **http://127.0.0.1:5000/admin/login**

- **Dashboard** — order/revenue stats
- **Products** — add / edit / remove menu items (each has name, cuisine, price, rating, delivery time, image URL, description)
- **Orders** — see every order placed on the site, filter by status, update status (Placed → Preparing → Out for Delivery → Delivered / Cancelled)

## 3. Public API (your frontend calls these)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/products` | List all active products. Supports `?search=` and `?cuisine=` |
| GET | `/api/products/<id>` | Single product |
| POST | `/api/orders` | Place an order (checkout) |
| GET | `/api/orders/<id>` | Track one order by ID |
| GET | `/api/orders?phone=...` | Get a customer's order history by phone number |

### POST /api/orders — request body
```json
{
  "customerName": "Ragu",
  "customerPhone": "9876543210",
  "customerEmail": "ragu@example.com",
  "address": "12 Main St, Salem",
  "items": [
    { "productId": 1, "quantity": 2 },
    { "productId": 3, "quantity": 1 }
  ]
}
```

## 4. Connecting your existing HTML/JS frontend

Your frontend is static files (opened via file:// or Live Server) — the API allows cross-origin requests (CORS is enabled), so you can `fetch()` it directly.

**Example — replace the hardcoded `restaurantsData` in `script.js`:**
```js
async function loadRestaurants() {
  const res = await fetch("http://127.0.0.1:5000/api/products");
  const data = await res.json();
  renderRestaurants(data);
}
```

**Example — checkout in `cart.html` (replace the localStorage-only `placeOrder`):**
```js
async function placeOrder(customerDetails) {
  const cart = getCart(); // [{id, name, priceValue, ...}, ...]

  const res = await fetch("http://127.0.0.1:5000/api/orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customerName: customerDetails.name,
      customerPhone: customerDetails.phone,
      address: customerDetails.address,
      items: cart.map(item => ({ productId: item.id, quantity: 1 }))
    })
  });

  const order = await res.json();
  saveCart([]); // clear local cart
  window.location.href = `orders.html?orderId=${order.id}`;
}
```

**Example — track/list orders in `orders.html`:**
```js
async function loadOrders(phone) {
  const res = await fetch(`http://127.0.0.1:5000/api/orders?phone=${phone}`);
  const orders = await res.json();
  renderOrders(orders);
}
```

> This step (wiring the exact HTML/JS in your files) isn't done yet — share `restaurants.html`'s render function, `cart.html`'s checkout flow, and `orders.html` when you're ready, and I'll make the exact edits so nothing breaks.

## 5. Project structure
```
backend/
├── app.py              # app factory, seeds default admin + starter products
├── config.py            # secret key, database path, default admin credentials
├── extensions.py        # shared db / login_manager instances
├── models.py             # Admin, Product, Order, OrderItem
├── requirements.txt
├── .env.example          # copy to .env and fill in for local overrides
├── instance/
│   └── ruchi.db         # SQLite database (auto-created)
├── routes/
│   ├── admin.py          # admin panel: auth, product CRUD, order management
│   └── api.py             # public API: products, orders
└── templates/admin/       # admin panel HTML pages
```

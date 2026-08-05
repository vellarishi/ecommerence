import secrets
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class Customer(db.Model):
    """A registered site customer (register.html / login.html), separate
    from Admin (which is only for the /admin panel). Auth uses a simple
    bearer token instead of cookie sessions — simpler to wire up from
    plain JS across pages opened via Live Server on different ports."""
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    auth_token = db.Column(db.String(64), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def generate_token(self):
        self.auth_token = secrets.token_hex(32)
        return self.auth_token

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
        }


class Admin(UserMixin, db.Model):
    """Admin panel login user. UserMixin gives Flask-Login the
    is_authenticated / get_id() etc. methods it needs."""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Product(db.Model):
    """A restaurant/dish listing — this is what index.html and
    restaurants.html will fetch from the API instead of using
    the hardcoded restaurantsData array in script.js."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cuisine = db.Column(db.String(80), nullable=False)
    price_value = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=4.0)
    delivery_time = db.Column(db.String(40), default="30-40 min")
    image_url = db.Column(db.String(500), default="")
    description = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cuisine": self.cuisine,
            "priceValue": self.price_value,
            "price": "₹" * min(max(self.price_value // 150, 1), 3),
            "rating": self.rating,
            "deliveryTime": self.delivery_time,
            "image": self.image_url,
            "description": self.description,
        }


class Order(db.Model):
    """One placed order — created when a customer checks out from cart.html."""
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    # Price breakdown — subtotal is the sum of line items; total is what the
    # customer actually pays (subtotal + delivery_fee + tax - discount).
    # Kept as separate columns (not just derived from `total`) so orders.html
    # and receipts can show exactly how the total was made up.
    subtotal = db.Column(db.Integer, nullable=False, default=0)
    delivery_fee = db.Column(db.Integer, nullable=False, default=0)
    tax = db.Column(db.Integer, nullable=False, default=0)
    discount = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.String(30), default="Placed"
    )

    # ---- NEW: payment details ----
    payment_method = db.Column(db.String(30), nullable=False, default="COD")   # 'COD', 'UPI', 'Card'
    amount_paid = db.Column(db.Integer, nullable=False, default=0)             # how much has actually been paid

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "customerName": self.customer_name,
            "customerEmail": self.customer_email,
            "customerPhone": self.customer_phone,
            "address": self.address,
            "subtotal": self.subtotal,
            "deliveryFee": self.delivery_fee,
            "tax": self.tax,
            "discount": self.discount,
            "total": self.total,
            "status": self.status,
            "paymentMethod": self.payment_method,   # NEW
            "amountPaid": self.amount_paid,         # NEW
            "date": self.created_at.strftime("%d/%m/%Y"),
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    """A line item inside an order. We snapshot product_name/price at
    order time so the order history stays correct even if the product
    is later edited or deleted from the admin panel."""
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    product_name = db.Column(db.String(120), nullable=False)
    price_value = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "productId": self.product_id,
            "name": self.product_name,
            "priceValue": self.price_value,
            "quantity": self.quantity,
        }
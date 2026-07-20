from flask import Blueprint, request, jsonify

from extensions import db
from models import Customer

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def get_customer_from_token():
    """Looks up the Customer for the bearer token on the request, if any.
    Used by routes/api.py to attach orders to a logged-in customer."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.removeprefix("Bearer ").strip()
    if not token:
        return None
    return Customer.query.filter_by(auth_token=token).first()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if Customer.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    customer = Customer(
        name=name,
        email=email,
        phone=(data.get("phone") or "").strip() or None,
        address=(data.get("address") or "").strip() or None,
    )
    customer.set_password(password)
    customer.generate_token()
    db.session.add(customer)
    db.session.commit()

    return jsonify({"token": customer.auth_token, "customer": customer.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    customer = Customer.query.filter_by(email=email).first()
    if not customer or not customer.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    customer.generate_token()
    db.session.commit()

    return jsonify({"token": customer.auth_token, "customer": customer.to_dict()})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    customer = get_customer_from_token()
    if customer:
        customer.auth_token = None
        db.session.commit()
    return jsonify({"success": True})


@auth_bp.route("/me", methods=["GET"])
def me():
    customer = get_customer_from_token()
    if not customer:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(customer.to_dict())

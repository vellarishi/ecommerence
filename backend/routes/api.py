from flask import Blueprint, request, jsonify
from extensions import db
from models import Product, Order, OrderItem
from routes.auth import get_customer_from_token

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ============================================================
# PRODUCTS — read-only for the public site
# (Editing happens only through /admin/products)
# ============================================================

@api_bp.route("/products", methods=["GET"])
def list_products():
    query = Product.query.filter_by(is_active=True)

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    cuisine = request.args.get("cuisine", "").strip()
    if cuisine and cuisine != "all":
        query = query.filter_by(cuisine=cuisine)

    products = query.order_by(Product.id).all()
    return jsonify([p.to_dict() for p in products])


@api_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())


# ============================================================
# ORDERS — create (checkout) + track
# ============================================================

@api_bp.route("/orders", methods=["POST"])
def create_order():
    """
    Expected JSON body (sent from cart.html checkout):
    {
      "customerName": "Ragu",
      "customerPhone": "9876543210",
      "customerEmail": "ragu@example.com",   (optional)
      "address": "12 Main St, Salem",
      "items": [{"productId": 1, "quantity": 2}, ...]
    }
    """
    data = request.get_json(silent=True) or {}

    # If the request carries a valid customer bearer token, link the
    # order to that account — this is what makes it show up under
    # "my orders" for a logged-in user without needing the phone lookup.
    customer = get_customer_from_token()

    name = (data.get("customerName") or "").strip() or (customer.name if customer else "")
    phone = (data.get("customerPhone") or "").strip() or (customer.phone if customer else "")
    address = (data.get("address") or "").strip() or (customer.address if customer else "")
    items_input = data.get("items") or []

    if not name or not phone or not address:
        return jsonify({"error": "customerName, customerPhone and address are required"}), 400
    if not items_input:
        return jsonify({"error": "Cart is empty — add at least one item"}), 400

    order = Order(
        customer_id=customer.id if customer else None,
        customer_name=name,
        customer_phone=phone,
        customer_email=(data.get("customerEmail") or "").strip() or (customer.email if customer else None),
        address=address,
        total=0,
        status="Placed",
    )
    db.session.add(order)

    subtotal = 0
    for entry in items_input:
        product = Product.query.get(entry.get("productId"))
        if not product:
            continue
        quantity = max(int(entry.get("quantity", 1)), 1)
        line_total = product.price_value * quantity
        subtotal += line_total

        order.items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            price_value=product.price_value,
            quantity=quantity,
        ))

    # Delivery is currently advertised as free (see cart.html); tax is a flat
    # 5% GST-style charge on the subtotal. No discount engine exists yet.
    delivery_fee = 0
    tax = round(subtotal * 0.05)
    discount = 0

    order.subtotal = subtotal
    order.delivery_fee = delivery_fee
    order.tax = tax
    order.discount = discount
    order.total = subtotal + delivery_fee + tax - discount
    db.session.commit()

    return jsonify(order.to_dict()), 201


@api_bp.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """Order tracking — cart.html/orders.html can poll this to show live status."""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@api_bp.route("/orders", methods=["GET"])
def list_orders_by_phone():
    """orders.html calls this with ?phone=... to show a customer's own order history."""
    phone = request.args.get("phone", "").strip()
    if not phone:
        return jsonify({"error": "Pass ?phone=... to look up orders"}), 400

    orders = Order.query.filter_by(customer_phone=phone).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@api_bp.route("/orders/me", methods=["GET"])
def list_my_orders():
    """orders.html calls this (with the Authorization header) for a
    logged-in customer — no need to type a phone number."""
    customer = get_customer_from_token()
    if not customer:
        return jsonify({"error": "Not logged in"}), 401

    orders = Order.query.filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])
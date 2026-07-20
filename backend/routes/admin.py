from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import Admin, Product, Order

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============================================================
# AUTH
# ============================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = Admin.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


# ============================================================
# DASHBOARD
# ============================================================

@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    stats = {
        "product_count": Product.query.filter_by(is_active=True).count(),
        "order_count": Order.query.count(),
        "pending_count": Order.query.filter(Order.status.in_(["Placed", "Preparing", "Out for Delivery"])).count(),
        "revenue": db.session.query(db.func.coalesce(db.func.sum(Order.total), 0))
            .filter(Order.status != "Cancelled").scalar(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_orders=recent_orders)


# ============================================================
# PRODUCTS — full CRUD
# ============================================================

@admin_bp.route("/products")
@login_required
def products():
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=all_products)


@admin_bp.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        product = Product(
            name=request.form.get("name", "").strip(),
            cuisine=request.form.get("cuisine", "").strip(),
            price_value=int(request.form.get("price_value", 0) or 0),
            rating=float(request.form.get("rating", 4.0) or 4.0),
            delivery_time=request.form.get("delivery_time", "30-40 min").strip(),
            image_url=request.form.get("image_url", "").strip(),
            description=request.form.get("description", "").strip(),
            is_active=True,
        )
        db.session.add(product)
        db.session.commit()
        flash(f'"{product.name}" added successfully.', "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=None)


@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.cuisine = request.form.get("cuisine", "").strip()
        product.price_value = int(request.form.get("price_value", 0) or 0)
        product.rating = float(request.form.get("rating", 4.0) or 4.0)
        product.delivery_time = request.form.get("delivery_time", "30-40 min").strip()
        product.image_url = request.form.get("image_url", "").strip()
        product.description = request.form.get("description", "").strip()
        product.is_active = request.form.get("is_active") == "on"
        db.session.commit()
        flash(f'"{product.name}" updated.', "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=product)


@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    # Soft delete — keeps past orders referencing this product intact.
    product.is_active = False
    db.session.commit()
    flash(f'"{product.name}" removed from the menu.', "success")
    return redirect(url_for("admin.products"))


# ============================================================
# ORDERS — view + update status (order tracking)
# ============================================================

@admin_bp.route("/orders")
@login_required
def orders():
    status_filter = request.args.get("status", "all")
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    all_orders = query.all()
    return render_template("admin/orders.html", orders=all_orders, status_filter=status_filter)


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    if new_status in ["Placed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} marked as {new_status}.", "success")
    return redirect(url_for("admin.orders"))

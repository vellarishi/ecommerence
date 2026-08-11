import os
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from config import Config
from extensions import db, login_manager
from models import Admin, Product


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Please log in to access the admin panel."

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.api import api_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        _seed_initial_data(app)

    return app


def _seed_initial_data(app):
    """Runs once on first launch: creates the default admin login and
    seeds 24 starter restaurants as real, editable Product rows —
    so the site has data from the very first run."""

    if Admin.query.count() == 0:
        admin = Admin(username=app.config["DEFAULT_ADMIN_USERNAME"])
        admin.set_password(app.config["DEFAULT_ADMIN_PASSWORD"])
        db.session.add(admin)
        print(f'[seed] Created admin login -> username: "{admin.username}"  '
              f'password: "{app.config["DEFAULT_ADMIN_PASSWORD"]}"  (change this!)')

    if Product.query.count() == 0:
        starter_products = [
            Product(name="Spice Garden", cuisine="South Indian", price_value=250,
                    rating=4.5, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1630383249896-424e482df921?w=600&h=400&fit=crop",
                    description="Classic South Indian tiffin and meals."),
            Product(name="Pizza Point", cuisine="Italian", price_value=450,
                    rating=4.2, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=400&fit=crop",
                    description="Wood-fired pizzas, pastas and garlic bread."),
            Product(name="Dragon Wok", cuisine="Chinese", price_value=300,
                    rating=4.0, delivery_time="35-45 min",
                    image_url="https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&h=400&fit=crop",
                    description="Indo-Chinese favourites — noodles, fried rice, Manchurian."),
            Product(name="Burger Bay", cuisine="Fast Food", price_value=150,
                    rating=4.3, delivery_time="20-30 min",
                    image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&h=400&fit=crop",
                    description="Burgers, fries and shakes."),
            Product(name="Coconut Curry House", cuisine="South Indian", price_value=280, rating=4.4, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1630383249896-424e482df921?w=600&h=400&fit=crop",
                    description="Kerala-style curries and dosas."),
            Product(name="Chettinad Express", cuisine="South Indian", price_value=320, rating=4.6, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1630383249896-424e482df921?w=600&h=400&fit=crop",
                    description="Spicy Chettinad specials."),
            Product(name="Punjabi Tadka", cuisine="North Indian", price_value=350, rating=4.5, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&h=400&fit=crop",
                    description="Rich North Indian gravies and tandoori."),
            Product(name="Delhi Darbar", cuisine="North Indian", price_value=380, rating=4.3, delivery_time="35-45 min",
                    image_url="https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&h=400&fit=crop",
                    description="Mughlai and Delhi street classics."),
            Product(name="Butter Chicken Co.", cuisine="North Indian", price_value=400, rating=4.7, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&h=400&fit=crop",
                    description="Famous for butter chicken and naan."),
            Product(name="Golden Dragon", cuisine="Chinese", price_value=310, rating=4.1, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&h=400&fit=crop",
                    description="Szechuan and Cantonese favourites."),
            Product(name="Wok This Way", cuisine="Chinese", price_value=290, rating=4.0, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&h=400&fit=crop",
                    description="Fried rice, noodles, and momos."),
            Product(name="Bella Italia", cuisine="Italian", price_value=480, rating=4.6, delivery_time="35-45 min",
                    image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=400&fit=crop",
                    description="Authentic pasta and wood-fired pizza."),
            Product(name="Roma Kitchen", cuisine="Italian", price_value=420, rating=4.4, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=400&fit=crop",
                    description="Classic Roman-style dishes."),
            Product(name="Pasta Palace", cuisine="Italian", price_value=390, rating=4.2, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=400&fit=crop",
                    description="Fresh handmade pasta daily."),
            Product(name="Green Bowl", cuisine="Healthy", price_value=260, rating=4.5, delivery_time="20-30 min",
                    image_url="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=400&fit=crop",
                    description="Salads, bowls, and protein plates."),
            Product(name="Fit Fuel Kitchen", cuisine="Healthy", price_value=300, rating=4.6, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=400&fit=crop",
                    description="Macro-balanced meals for fitness goals."),
            Product(name="Sweet Tooth", cuisine="Desserts", price_value=180, rating=4.7, delivery_time="20-30 min",
                    image_url="https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600&h=400&fit=crop",
                    description="Cakes, brownies, and pastries."),
            Product(name="The Dessert Lab", cuisine="Desserts", price_value=210, rating=4.5, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600&h=400&fit=crop",
                    description="Handcrafted desserts and shakes."),
            Product(name="Burger Barn", cuisine="Fast Food", price_value=170, rating=4.2, delivery_time="20-30 min",
                    image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&h=400&fit=crop",
                    description="Loaded burgers and crispy fries."),
            Product(name="Quick Bites", cuisine="Fast Food", price_value=160, rating=4.0, delivery_time="15-25 min",
                    image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&h=400&fit=crop",
                    description="Fast, fresh, and filling."),
            Product(name="Momo Magic", cuisine="Chinese", price_value=220, rating=4.3, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1585032226651-759b368d7246?w=600&h=400&fit=crop",
                    description="Steamed and fried momos, every style."),
            Product(name="Tandoor Nights", cuisine="North Indian", price_value=360, rating=4.4, delivery_time="30-40 min",
                    image_url="https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&h=400&fit=crop",
                    description="Tandoori kebabs and rotis."),
            Product(name="Dosa Junction", cuisine="South Indian", price_value=200, rating=4.3, delivery_time="20-30 min",
                    image_url="https://images.unsplash.com/photo-1630383249896-424e482df921?w=600&h=400&fit=crop",
                    description="50+ varieties of dosa."),
            Product(name="Cheesy Slice", cuisine="Italian", price_value=350, rating=4.1, delivery_time="25-35 min",
                    image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&h=400&fit=crop",
                    description="Stuffed-crust and thin-crust pizzas."),
        ]
        db.session.add_all(starter_products)
        print(f"[seed] Added {len(starter_products)} starter products.")

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("BACKEND_PORT", 5000))
    app.run(debug=True, port=port)
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
    carries over your existing 4 dummy restaurants as real, editable
    Product rows — so the site has data from the very first run."""

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
                    image_url="https://via.placeholder.com/300x200?text=Spice+Garden",
                    description="Classic South Indian tiffin and meals."),
            Product(name="Pizza Point", cuisine="Italian", price_value=450,
                    rating=4.2, delivery_time="25-35 min",
                    image_url="https://via.placeholder.com/300x200?text=Pizza+Point",
                    description="Wood-fired pizzas, pastas and garlic bread."),
            Product(name="Dragon Wok", cuisine="Chinese", price_value=300,
                    rating=4.0, delivery_time="35-45 min",
                    image_url="https://via.placeholder.com/300x200?text=Dragon+Wok",
                    description="Indo-Chinese favourites — noodles, fried rice, Manchurian."),
            Product(name="Burger Bay", cuisine="Fast Food", price_value=150,
                    rating=4.3, delivery_time="20-30 min",
                    image_url="https://via.placeholder.com/300x200?text=Burger+Bay",
                    description="Burgers, fries and shakes."),
        ]
        db.session.add_all(starter_products)
        print("[seed] Added 4 starter products.")

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("BACKEND_PORT", 5000))
    app.run(debug=True, port=port)
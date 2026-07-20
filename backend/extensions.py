from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Created here (not in app.py) so models.py and routes/*.py can import
# `db` and `login_manager` without importing the app factory itself —
# avoids circular imports.
db = SQLAlchemy()
login_manager = LoginManager()

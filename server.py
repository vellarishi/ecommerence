"""
Combined ASGI entrypoint for deployment (Render).

Render Web Services run a single process on a single port. This mounts the
Flask backend (backend/app.py) as a WSGI sub-application inside the FastAPI
chatbot service (chatbot-service/main.py), so both apps are served by one
uvicorn process. Local development is unaffected — run each service
separately as before (python backend/app.py / python chatbot-service/main.py).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "chatbot-service"))

from a2wsgi import WSGIMiddleware

from main import app as fastapi_app  # chatbot-service/main.py — registers /chat, /health, etc.
from app import create_app as create_flask_app  # backend/app.py

flask_app = create_flask_app()

# Catch-all: anything not matched by the FastAPI routes above (/api/*, /admin/*)
# falls through to the Flask app. Must be mounted after the FastAPI routes are
# registered (i.e. after `from main import app`) so those take priority.
fastapi_app.mount("/", WSGIMiddleware(flask_app))

app = fastapi_app

# Ruchi — Food Delivery E-commerce

## Structure

```
Ecommerce/
├── frontend/            # Static site (HTML/CSS/JS)
│   ├── *.html            # Pages: index, restaurants, cart, orders, login, ...
│   ├── css/               # style.css, style_1.css, navbar.css
│   └── js/                 # script.js, chatbot.js
├── backend/              # Flask API + admin panel (main backend)
│   ├── app.py              # App factory
│   ├── config.py
│   ├── extensions.py
│   ├── models.py           # Customer, Admin, Product, Order, OrderItem
│   ├── routes/              # admin, auth, api blueprints
│   ├── templates/admin/     # Server-rendered admin panel
│   ├── instance/             # SQLite DB (auto-created, gitignored)
│   └── requirements.txt
└── chatbot-service/       # Separate FastAPI microservice (RAG support chatbot)
    ├── main.py
    ├── rag_engine.py
    ├── escalation.py
    ├── knowledge_base.py
    └── requirements.txt
```

## Running it

**Frontend** — open `frontend/index.html` directly, or serve the folder with any static server (e.g. VS Code Live Server) from `frontend/`.

**Backend (Flask)**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # optional, edit as needed
python app.py
```
Runs at `http://127.0.0.1:5000`. See [backend/README.md](backend/README.md) for API docs and the admin panel.

**Chatbot service (FastAPI, optional)**
```bash
cd chatbot-service
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python main.py
```
Runs at `http://127.0.0.1:8000`.

## Notes

- The frontend currently runs standalone (cart/favorites use `localStorage`); wiring it up to call the Flask API is the next step — see section 4 of [backend/README.md](backend/README.md) for the exact `fetch()` calls to swap in.
- The chatbot service is independent of the main backend and kept on FastAPI by design.

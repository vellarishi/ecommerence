"""
Knowledge Base for Customer Support Chatbot
Contains Ruchi-specific FAQ and company information
"""

import re

from db_products import get_active_products

STATIC_KNOWLEDGE_BASE = [
    {
        "id": 1,
        "category": "Delivery",
        "question": "How long does delivery take?",
        "answer": "Most orders are delivered within 30-40 minutes, depending on the restaurant and your location in Salem.",
        "keywords": ["delivery", "time", "how long", "fast", "minutes"]
    },
    {
        "id": 4,
        "category": "Orders",
        "question": "How do I track my order?",
        "answer": "You can track your order using the phone number you placed it with, on the Orders page — just click 'Track My Order' in this chat and enter your number.",
        "keywords": ["track", "order", "status", "where"]
    },
    {
        "id": 5,
        "category": "Payment",
        "question": "What payment methods do you accept?",
        "answer": "Currently we support cash on delivery and UPI payments. Card payments are coming soon.",
        "keywords": ["payment", "pay", "method", "upi", "cash"]
    },
    {
        "id": 6,
        "category": "Account",
        "question": "Do I need an account to order?",
        "answer": "No account needed! You can order as a guest using just your name, phone number, and delivery address.",
        "keywords": ["account", "login", "register", "guest"]
    },
    {
        "id": 7,
        "category": "Company",
        "question": "Where does Ruchi deliver?",
        "answer": "We currently deliver across Salem and surrounding areas in Tamil Nadu, with plans to expand soon.",
        "keywords": ["deliver", "area", "location", "salem", "where"]
    },
    {
        "id": 8,
        "category": "Support",
        "question": "How can I contact support?",
        "answer": "You can reach us at hello@ruchi.app or +91 98765 43210, or use the Contact page on our website.",
        "keywords": ["contact", "support", "help", "phone", "email"]
    },
    {
        "id": 9,
        "category": "Orders",
        "question": "Can I modify or cancel my order?",
        "answer": "If your order hasn't been prepared yet, contact the restaurant directly or call our support at +91 98765 43210 to cancel or change it.",
        "keywords": ["cancel", "modify", "order", "change"]
    },
    {
        "id": 10,
        "category": "Products",
        "question": "Are the restaurants on Ruchi verified?",
        "answer": "Yes! Every restaurant on Ruchi is verified for hygiene and quality before being listed on our platform.",
        "keywords": ["verified", "genuine", "hygiene", "quality"]
    },
    {
        "id": 11,
        "category": "Payment",
        "question": "How much is the tax on my order?",
        "answer": "We charge a flat 5% tax on your order subtotal. Delivery is currently free, so your total is just the subtotal plus that 5% tax.",
        "keywords": ["tax", "gst", "price", "charge", "fee", "delivery fee"]
    }
]

def _build_product_knowledge() -> list:
    """Turns live rows from ruchi.db's products table into KB entries —
    one overview entry listing everything, plus one per restaurant — so
    answers stay correct as products are added/edited/removed via admin,
    instead of a hardcoded list going stale."""
    products = get_active_products()
    if not products:
        return []

    entries = []
    overview = ", ".join(f"{p['name']} ({p['cuisine']})" for p in products)
    entries.append({
        "id": "product-overview",
        "category": "Restaurants",
        "question": "What restaurants are available?",
        "answer": f"We currently feature {overview}, with more being added regularly.",
        "keywords": ["restaurant", "restaurants", "cuisine", "available", "options", "menu", "items", "dishes", "food"]
    })

    for p in products:
        details = f"{p['name']} serves {p['cuisine']} cuisine"
        if p.get("description"):
            details += f" — {p['description']}"
        details += f", rated {p['rating']} stars with {p['delivery_time']} delivery (₹{p['price_value']})."
        entries.append({
            "id": f"product-{p['name']}",
            "category": "Restaurants",
            "question": f"What does {p['name']} serve?",
            "answer": details,
            "keywords": [p["name"].lower(), p["cuisine"].lower()]
        })

    return entries


def get_all_knowledge():
    """Return all knowledge base entries: static FAQ + live product data."""
    return STATIC_KNOWLEDGE_BASE + _build_product_knowledge()

_WORD_RE = re.compile(r"\w+")

# "ruchi" and generic question/filler words appear in almost every KB entry's
# question, so counting them as matches drowns out the one word that's
# actually discriminating (e.g. "items") and leaves ties decided by list
# order instead of relevance. Stripped from the QUERY only — target text
# stays intact since matching against it isn't the problem.
_STOPWORDS = {
    "ruchi", "a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
    "have", "has", "had", "this", "that", "these", "those", "what", "which",
    "who", "whom", "how", "when", "where", "why", "having", "i", "you", "your",
    "yours", "me", "my", "mine", "we", "our", "it", "its", "to", "of", "in",
    "on", "for", "with", "and", "or", "so", "please", "can", "could", "would",
    "tell", "about", "abt",
}


def _words(text: str) -> set:
    return set(_WORD_RE.findall(text.lower()))


def _query_words(text: str) -> set:
    return _words(text) - _STOPWORDS


def search_knowledge(query: str) -> list:
    """
    Search knowledge base by matching whole words with the query.
    Returns list of relevant articles.
    """
    query_words = _query_words(query)
    results = []
    knowledge_base = get_all_knowledge()

    for article in knowledge_base:
        question_words = _words(article["question"])
        answer_words = _words(article["answer"])
        keyword_words = set()
        for keyword in article["keywords"]:
            keyword_words |= _words(keyword)

        score = 0
        for word in query_words:
            if word in question_words:
                score += 3
            if word in answer_words:
                score += 2
            if word in keyword_words:
                score += 2

        if score > 0:
            results.append((article, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [article for article, score in results]
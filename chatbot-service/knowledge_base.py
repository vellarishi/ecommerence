"""
Knowledge Base for Customer Support Chatbot
Contains Ruchi-specific FAQ and company information
"""

KNOWLEDGE_BASE = [
    {
        "id": 1,
        "category": "Delivery",
        "question": "How long does delivery take?",
        "answer": "Most orders are delivered within 30-40 minutes, depending on the restaurant and your location in Salem.",
        "keywords": ["delivery", "time", "how long", "fast", "minutes"]
    },
    {
        "id": 2,
        "category": "Restaurants",
        "question": "What restaurants are available?",
        "answer": "We currently feature Spice Garden (South Indian), Pizza Point (Italian), Dragon Wok (Chinese), and Burger Bay (Fast Food), with more being added regularly.",
        "keywords": ["restaurant", "restaurants", "cuisine", "available", "options"]
    },
    {
        "id": 3,
        "category": "Restaurants",
        "question": "What does Spice Garden serve?",
        "answer": "Spice Garden serves classic South Indian tiffin and meals — dosas, idlis, and traditional thalis, rated 4.5 stars with 30-40 min delivery.",
        "keywords": ["spice garden", "south indian", "taste", "menu"]
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
    }
]

def get_all_knowledge():
    """Return all knowledge base entries"""
    return KNOWLEDGE_BASE

def search_knowledge(query: str) -> list:
    """
    Search knowledge base by matching keywords with query
    Returns list of relevant articles
    """
    query_words = query.lower().split()
    results = []

    for article in KNOWLEDGE_BASE:
        score = 0
        for word in query_words:
            if word in article["question"].lower():
                score += 3
            if word in article["answer"].lower():
                score += 2
            for keyword in article["keywords"]:
                if word in keyword.lower():
                    score += 2

        if score > 0:
            results.append((article, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [article for article, score in results]
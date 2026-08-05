"""
RAG (Retrieval-Augmented Generation) Engine
Handles document retrieval (HF Inference API embeddings) and LLM integration (Groq)
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import InferenceClient
from openai import OpenAI
from dotenv import load_dotenv
from knowledge_base import get_all_knowledge, search_knowledge
from db_orders import get_orders_for_token

load_dotenv(Path(__file__).resolve().parent / ".env")


def _to_sentence_vector(raw_embedding) -> np.ndarray:
    """
    Normalize whatever the HF API returns into a single 1D sentence vector.
    The feature-extraction endpoint sometimes returns one vector per TOKEN
    instead of one per SENTENCE — if we don't mean-pool that down to one
    vector, similarity comparisons come out meaningless. This guarantees
    every embedding we compare is the same shape, computed the same way.
    """
    arr = np.array(raw_embedding, dtype=float)
    if arr.ndim == 1:
        return arr
    elif arr.ndim == 2:
        return arr.mean(axis=0)
    else:
        return arr.reshape(-1)


class RAGEngine:
    def __init__(self, api_key: Optional[str] = None):
        """
        Embeddings: Hugging Face Inference API (no local torch — avoids the
        Windows DLL crash entirely, since nothing runs on this machine).

        Generation: Groq's OpenAI-compatible API — kept as-is, this part
        was already working.
        """
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.embed_client = InferenceClient(api_key=os.environ["HF_TOKEN"])

        self.model = "llama-3.1-8b-instant"
        self.client = OpenAI(
            api_key=api_key or os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )

        self.knowledge_base = get_all_knowledge()
        self._initialize_vectorizer()

    def _initialize_vectorizer(self):
        """Pre-compute SEMANTIC EMBEDDINGS for every KB entry, once, at startup."""
        documents = []
        for doc in self.knowledge_base:
            combined_text = f"{doc['question']} {doc['answer']}"
            documents.append(combined_text)

        self.doc_vectors = np.array([
            _to_sentence_vector(
                self.embed_client.feature_extraction(text, model=self.embedding_model)
            )
            for text in documents
        ])

    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve top-k most relevant documents using SEMANTIC similarity."""
        keyword_results = search_knowledge(query)

        query_vector = _to_sentence_vector(
            self.embed_client.feature_extraction(query, model=self.embedding_model)
        ).reshape(1, -1)

        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        retrieved_docs = []
        seen_ids = set()

        for idx in top_indices:
            if similarities[idx] > 0:
                doc = self.knowledge_base[idx]
                if doc['id'] not in seen_ids:
                    retrieved_docs.append({
                        **doc,
                        "similarity_score": float(similarities[idx])
                    })
                    seen_ids.add(doc['id'])

        for doc in keyword_results[:top_k]:
            if doc['id'] not in seen_ids:
                retrieved_docs.append({
                    **doc,
                    "similarity_score": 0.7
                })
                seen_ids.add(doc['id'])

        return retrieved_docs[:top_k]

    def generate_response(self, query: str, retrieved_docs: List[Dict], order_context: Optional[str] = None) -> Dict:
        """Generate response using Groq with retrieved context"""
        try:
            context = ""
            for i, doc in enumerate(retrieved_docs, 1):
                context += f"\n{i}. Q: {doc['question']}\nA: {doc['answer']}"

            system_prompt = """You are a customer support assistant for Ruchi.
If an "Order History" section is provided below, that IS the customer's real data — it always answers order questions (count, status, totals, items, etc.). Answer directly from it FIRST, in one or two plain sentences, in your own words — never paste the raw "status ..., total ..., placed ..., items ..." formatting verbatim. Never claim you lack order information when an Order History section is present.
Do not also add unrelated general knowledge-base info (like generic "how to track an order" instructions) once you've already answered from Order History — only include knowledge-base content if it adds something the customer actually asked about.
When there is no Order History and the knowledge base contains a direct answer to the customer's question, respond using the EXACT wording from the knowledge base answer — do not paraphrase, summarize, or add extra commentary. Only rephrase slightly for grammar if the knowledge base text is copied word-for-word into your response.
If neither the knowledge base nor the order history answers the question, say so clearly and suggest escalation to human support.
Keep responses concise — do not add greetings like "Hello! I'd be happy to help" before the answer."""

            order_section = f"\n\nOrder History (this customer's real, confirmed orders — answer from this first, in your own words):\n{order_context}" if order_context else ""

            user_prompt = f"""Customer Query: {query}

Available Knowledge Base:
{context}{order_section}

Please provide a helpful response to the customer query. If Order History is present above, that is the answer — lead with it, phrased naturally, and don't tack on unrelated knowledge-base info.
Otherwise base your answer on the knowledge base, and if that doesn't answer it either, politely inform the customer and suggest they contact support."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2 if order_context else 0.7
            )

            return {
                "response": response.choices[0].message.content,
                "retrieved_docs": retrieved_docs,
                "success": True,
                "confidence": self._calculate_confidence(retrieved_docs)
            }

        except Exception as e:
            if retrieved_docs:
                top = retrieved_docs[0]
                return {
                    "response": top["answer"],
                    "retrieved_docs": retrieved_docs,
                    "success": True,
                    "confidence": self._calculate_confidence(retrieved_docs),
                    "error": str(e)
                }
            return {
                "response": "I'm having trouble reaching our AI assistant right now. Please try again shortly or contact support at +91 98765 43210.",
                "retrieved_docs": [],
                "success": True,
                "confidence": 0.0,
                "error": str(e)
            }

    def _calculate_confidence(self, retrieved_docs: List[Dict]) -> float:
        """Confidence reflects how good the best match is."""
        if not retrieved_docs:
            return 0.0
        top_similarity = max(doc.get("similarity_score", 0) for doc in retrieved_docs)
        return min(float(top_similarity), 1.0)

    def process_query(self, query: str, token: Optional[str] = None) -> Dict:
        """
        Complete RAG pipeline: retrieve + generate.
        High-confidence KB matches skip the LLM and return the exact KB answer —
        but only when there's no order context to weigh in, since that shortcut
        would otherwise return a canned FAQ answer instead of the customer's
        actual order data.
        """
        order_context = None
        query_lower = query.lower()
        # Broad net on purpose — catches "dishes", "spent", typos like "orderd",
        # etc. — so the LLM gets real data for any order-adjacent phrasing
        # instead of relying on ever-growing regex on the frontend.
        if token and any(w in query_lower for w in
                         ("order", "dish", "item", "spent", "spend", "bought",
                          "flavour", "flavor", "food", "meal", "ate", "eat",
                          "subtotal", "tax", "gst", "price", "cost", "amount",
                          "total", "bill", "charge", "delivery fee")):
            orders = get_orders_for_token(token)
            if orders:
                lines = []
                for o in orders:
                    items_desc = ", ".join(
                        f"{it['product_name']} x{it['quantity']}" for it in o.get("items", [])
                    ) or "no item details on file"
                    placed = str(o['created_at']).split(".")[0]
                    lines.append(
                        f"- Order #{o['id']}: status {o['status']}, subtotal ₹{o['subtotal']}, "
                        f"delivery fee ₹{o['delivery_fee']}, tax ₹{o['tax']}, discount ₹{o['discount']}, "
                        f"total ₹{o['total']}, placed {placed}, items: {items_desc}"
                    )
                order_context = f"{len(orders)} order(s) on file:\n" + "\n".join(lines)
            else:
                order_context = "No orders on file for this customer."

        retrieved_docs = self.retrieve_relevant_documents(query)

        if not order_context and retrieved_docs and retrieved_docs[0].get("similarity_score", 0) >= 0.6:
            return {
                "response": retrieved_docs[0]["answer"],
                "retrieved_docs": retrieved_docs,
                "success": True,
                "confidence": self._calculate_confidence(retrieved_docs)
            }

        result = self.generate_response(query, retrieved_docs, order_context=order_context)
        return result
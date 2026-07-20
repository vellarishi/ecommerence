"""
RAG (Retrieval-Augmented Generation) Engine
Handles document retrieval and LLM integration (Hugging Face Inference API)
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from knowledge_base import get_all_knowledge, search_knowledge

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class RAGEngine:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize RAG Engine with Hugging Face Inference API"""
        self.model = "meta-llama/Llama-3.2-3B-Instruct:featherless-ai"
        self.client = InferenceClient(api_key=api_key or os.environ["HF_TOKEN"])
        self.knowledge_base = get_all_knowledge()
        self._initialize_vectorizer()

    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer for document retrieval"""
        documents = []
        for doc in self.knowledge_base:
            combined_text = f"{doc['question']} {doc['answer']}"
            documents.append(combined_text)

        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant documents using TF-IDF similarity
        """
        keyword_results = search_knowledge(query)

        query_vector = self.vectorizer.transform([query])
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

    def generate_response(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """
        Generate response using Hugging Face Inference API with retrieved context
        """
        try:
            context = ""
            for i, doc in enumerate(retrieved_docs, 1):
                context += f"\n{i}. Q: {doc['question']}\nA: {doc['answer']}"

            system_prompt = """You are a customer support assistant for Ruchi.
When the knowledge base contains a direct answer to the customer's question, respond using the EXACT wording from the knowledge base answer — do not paraphrase, summarize, or add extra commentary.
Only rephrase slightly for grammar if the knowledge base text is copied word-for-word into your response.
If the knowledge base has no relevant answer, say so clearly and suggest escalation to human support.
Keep responses concise — do not add greetings like "Hello! I'd be happy to help" before the answer."""

            user_prompt = f"""Customer Query: {query}

Available Knowledge Base:
{context}

Please provide a helpful response to the customer query. Base your answer on the provided knowledge base.
If the query cannot be answered from the knowledge base, politely inform the customer and suggest they contact support."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )

            return {
                "response": response.choices[0].message.content,
                "retrieved_docs": retrieved_docs,
                "success": True,
                "confidence": self._calculate_confidence(retrieved_docs)
            }

        except Exception as e:
            # Hugging Face call failed (rate limit, network, etc). Rather than
            # failing the whole request, fall back to the best knowledge-base
            # match so the customer still gets an answer if we found one.
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
        """Confidence reflects how good the best match is — averaging in
        weaker 2nd/3rd matches would drag down a genuinely strong top hit."""
        if not retrieved_docs:
            return 0.0

        top_similarity = max(doc.get("similarity_score", 0) for doc in retrieved_docs)
        return min(float(top_similarity), 1.0)

    def process_query(self, query: str) -> Dict:
        """
        Complete RAG pipeline: retrieve + generate
        High-confidence matches skip the LLM and return the exact KB answer.
        """
        retrieved_docs = self.retrieve_relevant_documents(query)

        # High-confidence match → return exact KB answer, skip LLM
        if retrieved_docs and retrieved_docs[0].get("similarity_score", 0) >= 0.6:
            return {
                "response": retrieved_docs[0]["answer"],
                "retrieved_docs": retrieved_docs,
                "success": True,
                "confidence": self._calculate_confidence(retrieved_docs)
            }

        result = self.generate_response(query, retrieved_docs)
        return result
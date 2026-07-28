"""
FastAPI Backend for AI Customer Support Chatbot with RAG
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from the shared root .env before RAGEngine() reads GROQ_API_KEY
load_dotenv(Path(__file__).resolve().parent / ".env")

from rag_engine import RAGEngine
from escalation import EscalationEngine, EscalationCriteria

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Customer Support Chatbot API",
    description="AI-powered chatbot with RAG and escalation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
try:
    rag_engine = RAGEngine()
    escalation_engine = EscalationEngine()
    logger.info("RAG and Escalation engines initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize engines: {e}")
    # Create placeholder engines for testing without API key
    rag_engine = None
    escalation_engine = EscalationEngine()

# ========================== Request/Response Models ==========================

class ChatQuery(BaseModel):
    """User chat query"""
    message: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chatbot response"""
    response: str
    confidence: float
    retrieved_documents: List[dict] = []
    needs_escalation: bool = False
    escalation_info: Optional[dict] = None
    session_id: Optional[str] = None

class EscalationTicket(BaseModel):
    """Escalation ticket for human support"""
    ticket_id: str
    customer_query: str
    bot_response: str
    confidence_score: float
    escalation_reason: str
    priority: str
    department: str
    status: str

# ========================== Endpoints ==========================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Customer Support Chatbot",
        "rag_engine": "ready" if rag_engine else "not_initialized"
    }

@app.post("/chat", response_model=ChatResponse)
async def process_chat(query: ChatQuery, background_tasks: BackgroundTasks):
    """
    Process customer query and return AI response
    
    - Retrieves relevant documents using RAG
    - Generates response with OpenAI
    - Evaluates need for escalation
    - Optionally escalates to human support
    """
    
    if not query.message or not query.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # If RAG engine not initialized, provide fallback response
        if not rag_engine:
            return ChatResponse(
                response="I apologize, but the chatbot is not properly configured. Please contact our support team.",
                confidence=0.0,
                needs_escalation=True,
                escalation_info={
                    "reason": "Chatbot not initialized",
                    "priority": "high"
                },
                session_id=query.session_id
            )
        
        # Process query through RAG pipeline
        rag_result = rag_engine.process_query(query.message)
        
        if not rag_result["success"]:
            raise Exception(rag_result.get("error", "Unknown error"))
        
        response_text = rag_result["response"]
        confidence = rag_result["confidence"]
        retrieved_docs = rag_result.get("retrieved_docs", [])
        
        # Evaluate need for escalation
        escalation_result = escalation_engine.should_escalate(
            query=query.message,
            response=rag_result,
            confidence=confidence,
            session_id=query.session_id
        )
        
        result = ChatResponse(
            response=response_text,
            confidence=confidence,
            retrieved_documents=retrieved_docs,
            needs_escalation=escalation_result["should_escalate"],
            escalation_info=escalation_result if escalation_result["should_escalate"] else None,
            session_id=query.session_id
        )
        
        # If escalation needed, create ticket in background
        if escalation_result["should_escalate"]:
            background_tasks.add_task(
                create_escalation_ticket,
                query.message,
                rag_result,
                escalation_result,
                query.customer_id
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/escalate", response_model=EscalationTicket)
async def escalate_query(
    query: ChatQuery,
    reason: str,
    priority: str = "medium"
):
    """
    Manually escalate a query to human support
    """
    
    try:
        ticket = escalation_engine.create_escalation_ticket(
            query=query.message,
            response={"response": "Query escalated by user", "confidence": 0},
            escalation_info={
                "should_escalate": True,
                "reasons": [reason],
                "priority": priority,
                "suggested_department": "general_support",
                "timestamp": ""
            }
        )
        
        logger.info(f"Escalation ticket created: {ticket['ticket_id']}")
        return EscalationTicket(**ticket)
    
    except Exception as e:
        logger.error(f"Error creating escalation ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@app.get("/knowledge-base")
async def get_knowledge_base():
    """Retrieve all knowledge base articles"""
    try:
        from knowledge_base import get_all_knowledge
        return {
            "total_articles": len(get_all_knowledge()),
            "articles": get_all_knowledge()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-knowledge")
async def search_knowledge(q: str):
    """Search knowledge base"""
    try:
        from knowledge_base import search_knowledge
        results = search_knowledge(q)
        return {
            "query": q,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================== Background Tasks ==========================

async def create_escalation_ticket(query: str, response: dict, escalation_info: dict, customer_id: str = None):
    """Create escalation ticket and log to system"""
    try:
        ticket = escalation_engine.create_escalation_ticket(query, response, escalation_info)
        logger.info(f"Escalation ticket {ticket['ticket_id']} created for customer {customer_id}")
        # In production, save this to database/queue for human agents to review
    except Exception as e:
        logger.error(f"Error creating escalation ticket: {e}")

# ========================== Root Endpoint ==========================

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "message": "Customer Support Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "escalate": "/escalate (POST)",
            "knowledge_base": "/knowledge-base (GET)",
            "search": "/search-knowledge (GET)",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("CHATBOT_PORT", 8000)))

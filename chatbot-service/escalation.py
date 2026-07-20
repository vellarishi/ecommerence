"""
Escalation Logic for Customer Support Chatbot
Determines when to escalate queries to human agents
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EscalationCriteria:
    """Criteria for escalating to human support"""
    low_confidence_threshold: float = 0.3
    customer_frustration_keywords: List[str] = None
    escalation_reasons: List[str] = None
    
    def __post_init__(self):
        if self.customer_frustration_keywords is None:
            self.customer_frustration_keywords = [
                "angry", "frustrated", "upset", "terrible", "worst",
                "unacceptable", "bad", "poor", "disappointed", "help"
            ]
        if self.escalation_reasons is None:
            self.escalation_reasons = []

class EscalationEngine:
    def __init__(self, criteria: EscalationCriteria = None):
        self.criteria = criteria or EscalationCriteria()
        self.escalation_count = {}  # Track escalations per session
    
    def should_escalate(self, 
                       query: str, 
                       response: Dict, 
                       confidence: float,
                       session_id: str = None) -> Dict:
        """
        Determine if a query should be escalated to human support
        
        Returns:
            {
                "should_escalate": bool,
                "reason": str,
                "priority": "low" | "medium" | "high",
                "suggested_department": str
            }
        """
        reasons = []
        priority = "low"
        
        # Check 1: Low confidence score
        if confidence < self.criteria.low_confidence_threshold:
            reasons.append(f"Low confidence in answer (confidence: {confidence:.2f})")
            priority = "medium"
        
        # Check 2: Detect frustration in customer message
        frustration_detected = self._detect_frustration(query)
        if frustration_detected:
            reasons.append("Customer frustration detected")
            priority = "high"
        
        # Check 3: Query seems to require special handling
        special_handling = self._check_special_handling(query)
        if special_handling:
            reasons.append(special_handling)
            priority = "high"
        
        # Check 4: Response indicates escalation needed
        if not response.get("success", True):
            reasons.append("System error in generating response")
            priority = "medium"
        
        # Check 5: Multiple failed attempts (from session tracking)
        if session_id and self._check_repeated_queries(session_id):
            reasons.append("Customer has asked similar questions multiple times")
            priority = "high"
        
        should_escalate = len(reasons) > 0
        
        return {
            "should_escalate": should_escalate,
            "reasons": reasons,
            "priority": priority,
            "suggested_department": self._suggest_department(query),
            "timestamp": datetime.now().isoformat()
        }
    
    def _detect_frustration(self, query: str) -> bool:
        """Detect signs of customer frustration in query"""
        query_lower = query.lower()
        
        # Check for frustration keywords
        for keyword in self.criteria.customer_frustration_keywords:
            if keyword in query_lower:
                return True
        
        # Check for multiple punctuation marks (!!!???)
        if query.count("!") >= 2 or query.count("?") >= 2:
            return True
        
        # Check for ALL CAPS words (multiple)
        caps_words = len([word for word in query.split() if word.isupper()])
        if caps_words >= 2:
            return True
        
        return False
    
    def _check_special_handling(self, query: str) -> str:
        """Check if query requires special handling"""
        query_lower = query.lower()
        
        # Billing/Payment issues
        if any(word in query_lower for word in ["refund", "payment", "billing", "charge"]):
            return "Billing/Payment issue - requires account access"
        
        # Security issues
        if any(word in query_lower for word in ["hacked", "stolen", "security", "compromised", "suspicious"]):
            return "Security concern - requires immediate attention"
        
        # Legal/Compliance
        if any(word in query_lower for word in ["lawsuit", "legal", "attorney", "compliance"]):
            return "Legal matter - requires specialized handling"
        
        # Complaint/Negative feedback
        if any(word in query_lower for word in ["complaint", "never buy", "worst", "terrible", "scam"]):
            return "Customer complaint - priority handling needed"
        
        return ""
    
    def _check_repeated_queries(self, session_id: str) -> bool:
        """Check if customer has asked similar questions multiple times"""
        if session_id not in self.escalation_count:
            self.escalation_count[session_id] = 0
        
        self.escalation_count[session_id] += 1
        
        # Escalate if same session has 3+ queries
        return self.escalation_count[session_id] >= 3
    
    def _suggest_department(self, query: str) -> str:
        """Suggest which department should handle the escalation"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["refund", "payment", "billing", "charge"]):
            return "billing_support"
        elif any(word in query_lower for word in ["deliver", "ship", "track", "order"]):
            return "shipping_support"
        elif any(word in query_lower for word in ["product", "quality", "defect", "broken"]):
            return "product_support"
        elif any(word in query_lower for word in ["account", "password", "login"]):
            return "account_support"
        elif any(word in query_lower for word in ["complaint", "angry", "frustrated"]):
            return "vip_support"
        else:
            return "general_support"
    
    def create_escalation_ticket(self, 
                                 query: str, 
                                 response: Dict,
                                 escalation_info: Dict) -> Dict:
        """Create a ticket for human support"""
        
        return {
            "ticket_id": f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customer_query": query,
            "bot_response": response.get("response", ""),
            "confidence_score": response.get("confidence", 0),
            "escalation_reason": ", ".join(escalation_info["reasons"]),
            "priority": escalation_info["priority"],
            "department": escalation_info["suggested_department"],
            "timestamp": escalation_info["timestamp"],
            "status": "pending_assignment"
        }

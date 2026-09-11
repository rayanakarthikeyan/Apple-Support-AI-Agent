"""
Data schema and domain models for the Customer Support AI Agent.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class Intent(str, Enum):
    TECH_TROUBLESHOOTING = "TECH_TROUBLESHOOTING"
    ACCOUNT_BILLING = "ACCOUNT_BILLING"
    HARDWARE_REPAIR = "HARDWARE_REPAIR"
    HOW_TO_QUERY = "HOW_TO_QUERY"
    STATUS_OUTAGE = "STATUS_OUTAGE"
    GENERAL_FEEDBACK_RANT = "GENERAL_FEEDBACK_RANT"


class EscalationDecision(str, Enum):
    AUTO_RESOLVE = "AUTO_RESOLVE"
    ESCALATE_SENSITIVE = "ESCALATE_SENSITIVE"     # PII, password, Apple ID locked, billing fraud
    ESCALATE_FRUSTRATED = "ESCALATE_FRUSTRATED"   # severe churn, anger, profanity, repeated failures
    ESCALATE_COMPLEX = "ESCALATE_COMPLEX"         # physical hardware breakdown, warranty inspection


@dataclass
class CustomerMessage:
    id: str
    text: str
    author_id: str = "customer_user"
    created_at: Optional[str] = None
    thread_history: List[str] = field(default_factory=list)


@dataclass
class ResolutionExemplar:
    id: str
    customer_text: str
    brand_reply: str
    intent: Intent
    source: str = "historical_twitter"
    tags: List[str] = field(default_factory=list)


@dataclass
class AgentOutput:
    message_id: str
    intent: Intent
    intent_confidence: float
    escalate: bool
    escalation_decision: EscalationDecision
    escalation_reason: str
    drafted_reply: str
    retrieved_exemplar_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["intent"] = self.intent.value
        d["escalation_decision"] = self.escalation_decision.value
        return d


@dataclass
class GoldEvaluationItem:
    id: str
    customer_text: str
    gold_intent: Intent
    gold_escalate: bool
    gold_escalation_decision: EscalationDecision
    gold_escalation_reason: str
    gold_reference_reply: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["gold_intent"] = self.gold_intent.value
        d["gold_escalation_decision"] = self.gold_escalation_decision.value
        return d

import json
from typing import List, Optional
from src.agent.models import CustomerMessage, AgentOutput, ResolutionExemplar, Intent, EscalationDecision
from src.classifier.rule_classifier import RuleBasedClassifier
from src.router.escalation_router import EscalationRouter
from src.retrieval.bm25 import BM25Retriever

class TrivialBaselineAgent:
    def process(self, message: CustomerMessage) -> AgentOutput:
        escalate = len(message.text) > 150
        decision = EscalationDecision.ESCALATE_FRUSTRATED if escalate else EscalationDecision.AUTO_RESOLVE
        reason = 'Message length threshold' if escalate else 'Default macro'
        reply = 'Thanks for reaching out! Please DM us your device model and iOS version: https://twitter.com/messages/compose?recipient_id=AppleSupport ^Support'
        return AgentOutput(
            message_id=message.id,
            intent=Intent.TECH_TROUBLESHOOTING,
            intent_confidence=0.33,
            escalate=escalate,
            escalation_decision=decision,
            escalation_reason=reason,
            drafted_reply=reply,
            metadata={'agent_type': 'trivial_baseline'}
        )

class SimpleBaselineAgent:
    def __init__(self):
        self.classifier = RuleBasedClassifier()

    def process(self, message: CustomerMessage) -> AgentOutput:
        intent, conf = self.classifier.predict(message.text)
        escalate = any(w in message.text.lower() for w in ['refund', 'hacked', 'lawyer', 'swollen', 'broken'])
        decision = EscalationDecision.ESCALATE_SENSITIVE if escalate else EscalationDecision.AUTO_RESOLVE
        reason = 'Simple keyword trigger' if escalate else 'Simple auto-resolve'
        reply = f'Hello! We understand you have an issue related to {intent.value}. Please check Apple Support at https://support.apple.com. ^Apple'
        return AgentOutput(
            message_id=message.id,
            intent=intent,
            intent_confidence=conf,
            escalate=escalate,
            escalation_decision=decision,
            escalation_reason=reason,
            drafted_reply=reply,
            metadata={'agent_type': 'simple_baseline'}
        )

class ProductionSupportAgent:
    def __init__(self, historical_exemplars_path: str = 'data/raw/historical_apple_support_exemplars.json'):
        self.classifier = RuleBasedClassifier()
        self.router = EscalationRouter()
        self.retriever = BM25Retriever()

        with open(historical_exemplars_path, 'r', encoding='utf-8') as f:
            raw_exemplars = json.load(f)

        self.exemplars = []
        for idx, ex in enumerate(raw_exemplars):
            self.exemplars.append(ResolutionExemplar(
                id=f'ex_{idx:03d}',
                customer_text=ex['customer'],
                brand_reply=ex['reply'],
                intent=Intent(ex['intent']),
                tags=ex.get('tags', [])
            ))

        self.retriever.fit(self.exemplars)

    def process(self, message: CustomerMessage) -> AgentOutput:
        predicted_intent, confidence = self.classifier.predict(message.text)
        escalate, decision, reason = self.router.route(message.text, predicted_intent)
        retrieved = self.retriever.retrieve(message.text, top_k=2, intent_filter=predicted_intent)
        retrieved_ids = [r[0].id for r in retrieved]

        if retrieved:
            top_match, score = retrieved[0]
            drafted_reply = top_match.brand_reply
        else:
            drafted_reply = 'We are here to help! Please check our support guides at https://support.apple.com. ^AppleSupport'
        return AgentOutput(
            message_id=message.id,
            intent=predicted_intent,
            intent_confidence=confidence,
            escalate=escalate,
            escalation_decision=decision,
            escalation_reason=reason,
            drafted_reply=drafted_reply,
            retrieved_exemplar_ids=retrieved_ids,
            metadata={'agent_type': 'production_support_agent'}
        )

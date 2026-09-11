import re
from typing import Tuple
from src.agent.models import EscalationDecision, Intent

class EscalationRouter:
    PII_AND_SECURITY_PATTERNS = [
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b',
        r'\bcard ending in \d{4}\b',
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\bapple id.*locked\b',
        r'\bhacked\b',
        r'\bunauthorized charge\b',
        r'\bfraud\b',
        r'\bsecurity lockout\b',
        r'\bphishing\b'
    ]

    FRUSTRATION_AND_LEGAL_PATTERNS = [
        r'\blawyer\b', r'\blawsuit\b', r'\battorney\b', r'\blegal action\b',
        r'\bsue\b', r'\bsuing\b',
        r'\bsupervisor\b', r'\bmanager\b',
        r'\bhung up\b', r'\blied\b', r'\bdisgusted\b',
        r'\bfire your\b', r'\bexecutive\b',
        r'\bfiling a complaint\b'
    ]

    COMPLEX_HARDWARE_PATTERNS = [
        r'\bbulging\b', r'\bswollen\b', r'\bsmelling\b', r'\bchemical\b',
        r'\bthermal\b', r'\bfire\b', r'\bsmoke\b',
        r'\bgreen line\b', r'\bboot loop\b', r'\bwhite apple logo\b',
        r'\bliquid\b', r'\bsalt water\b', r'\bwater damage\b', r'\bcorrosion\b',
        r'\bblack screen\b'
    ]

    def route(self, text: str, predicted_intent: Intent) -> Tuple[bool, EscalationDecision, str]:
        text_lower = text.lower()

        for pat in self.PII_AND_SECURITY_PATTERNS:
            if re.search(pat, text_lower):
                return (True, EscalationDecision.ESCALATE_SENSITIVE, 'PII or security matter detected; requires secure DM.')

        for pat in self.FRUSTRATION_AND_LEGAL_PATTERNS:
            if re.search(pat, text_lower):
                return (True, EscalationDecision.ESCALATE_FRUSTRATED, 'Severe frustration or legal threat requiring Senior Advisor.')

        for pat in self.COMPLEX_HARDWARE_PATTERNS:
            if re.search(pat, text_lower):
                return (True, EscalationDecision.ESCALATE_COMPLEX, 'Hardware safety hazard or diagnostic inspection required.')

        return (False, EscalationDecision.AUTO_RESOLVE, 'Standard inquiry addressable through public support.')

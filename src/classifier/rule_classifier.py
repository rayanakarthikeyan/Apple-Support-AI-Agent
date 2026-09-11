import re
from typing import Tuple, Dict
from src.agent.models import Intent

class RuleBasedClassifier:
    PATTERNS: Dict[Intent, list] = {
        Intent.ACCOUNT_BILLING: [
            r'\bcharge[ds]?\b', r'\bbill(?:ing)?\b', r'\bapple\.com/bill\b', r'\brefund\b',
            r'\bsubscription\b', r'\bcredit card\b', r'\bdebit card\b', r'\bapple id\b',
            r'\biforgot\b', r'\blocked\b', r'\bpassword\b', r'\bphishing\b', r'\bhacked\b',
            r'\bpayment\b', r'\bpurchase[sd]?\b', r'\broblox\b', r'\bin-app purchase\b'
        ],
        Intent.HARDWARE_REPAIR: [
            r'\bscreen\b.*\b(cracked|shattered|broken|damage)\b',
            r'\b(cracked|shattered|broken)\b.*\bscreen\b',
            r'\bback glass\b', r'\bbulging\b', r'\bswollen\b', r'\blithium\b',
            r'\bliquid\b', r'\bspill(?:ed)?\b', r'\bwater\b', r'\bsalt water\b',
            r'\bgenius bar\b', r'\brepair\b', r'\btrade-in\b', r'\btrade in\b',
            r'\bcost to replace\b', r'\breplace the battery\b'
        ],
        Intent.STATUS_OUTAGE: [
            r'\bdown right now\b', r'\bis.*down\b', r'\boutage\b', r'\bserver connection\b',
            r'\bsystem status\b', r'\berror 503\b', r'\bnot loading\b.*\bserver\b',
            r'\bdown today\b', r'\bglobal outage\b', r'\bmessages going green\b'
        ],
        Intent.HOW_TO_QUERY: [
            r'\bhow do i\b', r'\bhow to\b', r'\bcan i\b', r'\bhow can i\b',
            r'\bmove to ios\b', r'\bquick start\b', r'\btransfer\b.*\b(data|photos|contacts)\b',
            r'\bturn on\b', r'\benable\b', r'\bactivate\b', r'\bback up\b',
            r'\bmanually back up\b', r'\bfamily sharing\b', r'\bdual sim\b'
        ],
        Intent.GENERAL_FEEDBACK_RANT: [
            r'\bhate\b', r'\bgarbage\b', r'\bunusable\b', r'\bugly\b', r'\bwho approved\b',
            r'\bfire your\b', r'\brude\b', r'\bhung up\b', r'\blied\b', r'\blawyer\b',
            r'\blawsuit\b', r'\battorney\b', r'\bcorporate greed\b', r'\brip steve jobs\b',
            r'\bworst\b', r'\bterrible\b', r'\bsupervisor\b', r'\bdisgusted\b'
        ],
        Intent.TECH_TROUBLESHOOTING: [
            r'\bbattery\b.*\b(drain|draining|drained|fast)\b',
            r'\bdrain\b', r'\bmicrophone\b', r'\bmic\b', r'\bspeaker\b', r'\bhear me\b',
            r'\bsystem data\b', r'\bother storage\b', r'\bboot loop\b', r'\bapple logo\b',
            r'\bgreen line\b', r'\bflickering\b', r'\bfreeze\b', r'\bcrashing\b',
            r'\bcarplay\b', r'\bbluetooth\b', r'\bairpods\b', r'\bwifi\b', r'\bwi-fi\b',
            r'\bdisconnecting\b', r'\bnot working\b', r'\bglitch\b', r'\bbug\b'
        ]
    }

    def predict(self, text: str) -> Tuple[Intent, float]:
        text_lower = text.lower()
        scores = {intent: 0 for intent in Intent}

        for intent, patterns in self.PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    scores[intent] += 1

        best_intent = Intent.TECH_TROUBLESHOOTING
        best_score = -1
        total_hits = sum(scores.values())

        for intent in [
            Intent.ACCOUNT_BILLING,
            Intent.HARDWARE_REPAIR,
            Intent.STATUS_OUTAGE,
            Intent.GENERAL_FEEDBACK_RANT,
            Intent.HOW_TO_QUERY,
            Intent.TECH_TROUBLESHOOTING
        ]:
            if scores[intent] > best_score:
                best_score = scores[intent]
                best_intent = intent

        confidence = (best_score / max(1, total_hits)) if total_hits > 0 else 0.5
        return best_intent, min(1.0, max(0.4, confidence))

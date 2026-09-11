from typing import Dict, Any, List

class LLMAsAJudgeRubric:
    @staticmethod
    def evaluate_reply(customer_query: str, agent_reply: str, reference_reply: str,
                       agent_escalate: bool, gold_escalate: bool) -> Dict[str, Any]:
        query_l = customer_query.lower()
        reply_l = agent_reply.lower()

        # 1. Factual Grounding & Policy Adherence
        grounding_score = 5
        has_apple_domain = 'apple.co' in reply_l or 'apple.com' in reply_l
        if not has_apple_domain and ('how' in query_l or 'update' in query_l):
            grounding_score = 3
        if 'dm' in reply_l and not gold_escalate and ('cancel' in query_l or 'turn on' in query_l):
            grounding_score = 3

        # 2. Tone, Empathy & Brand Voice
        tone_score = 5
        has_signoff = '^' in agent_reply
        has_polite_opening = any(w in reply_l for w in ['help', 'sorry', 'appreciate', 'understand', 'welcome', 'thanks'])
        if not has_signoff:
            tone_score -= 1
        if not has_polite_opening:
            tone_score -= 1

        # 3. Actionability & Troubleshooting Utility
        actionability_score = 5
        if 'settings >' not in reply_l and ('battery' in query_l or 'storage' in query_l or 'turn on' in query_l):
            actionability_score = 3
        if len(reply_l.split()) < 8:
            actionability_score = 2

        # 4. Escalation Appropriateness
        escalation_score = 5
        if agent_escalate != gold_escalate:
            escalation_score = 2
            if gold_escalate and not agent_escalate:
                escalation_score = 1

        # 5. Privacy & Safety Compliance
        safety_score = 5
        if 'reply with your serial' in reply_l or 'post your card' in reply_l or 'tweet your email' in reply_l:
            safety_score = 1
        if ('swollen' in query_l or 'bulging' in query_l) and ('stop using' not in reply_l and 'charging' not in reply_l):
            safety_score = 2

        overall_score = round((grounding_score + tone_score + actionability_score + escalation_score + safety_score) / 5.0, 2)

        return {
            'grounding': grounding_score,
            'tone_and_voice': tone_score,
            'actionability': actionability_score,
            'escalation_appropriateness': escalation_score,
            'safety_compliance': safety_score,
            'overall_score': overall_score
        }

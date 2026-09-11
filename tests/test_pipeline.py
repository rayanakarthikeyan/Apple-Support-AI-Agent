import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.curdir))

from src.agent.models import CustomerMessage, Intent, EscalationDecision
from src.agent.agent_pipeline import ProductionSupportAgent, TrivialBaselineAgent
from src.router.escalation_router import EscalationRouter

class TestAgentPipeline(unittest.TestCase):
    def setUp(self):
        self.agent = ProductionSupportAgent()
        self.router = EscalationRouter()

    def test_pii_escalation(self):
        msg = CustomerMessage(id='test1', text='@AppleSupport Someone charged my card ending in 4102 twice! Refund now!')
        out = self.agent.process(msg)
        self.assertTrue(out.escalate)
        self.assertEqual(out.escalation_decision, EscalationDecision.ESCALATE_SENSITIVE)

    def test_battery_swelling_safety_escalation(self):
        msg = CustomerMessage(id='test2', text='@AppleSupport My MacBook battery is bulging and swollen!')
        out = self.agent.process(msg)
        self.assertTrue(out.escalate)
        self.assertEqual(out.escalation_decision, EscalationDecision.ESCALATE_COMPLEX)

    def test_how_to_auto_resolve(self):
        msg = CustomerMessage(id='test3', text='@AppleSupport How do I turn on Night Shift on my iPad?')
        out = self.agent.process(msg)
        self.assertFalse(out.escalate)
        self.assertEqual(out.intent, Intent.HOW_TO_QUERY)

    def test_agent_signoff_format(self):
        msg = CustomerMessage(id='test4', text='@AppleSupport Is mystem down right now?')
        out = self.agent.process(msg)
        self.assertIn('^', out.drafted_reply)

if __name__ == '__main__':
    unittest.main()

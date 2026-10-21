import unittest
from eval.judge import HeuristicReplyRubric
from eval.run_eval import evaluate_system, load_gold_data
from src.agent.agent_pipeline import SimpleBaselineAgent

class EvaluationIntegrityTests(unittest.TestCase):
    def test_current_evaluation_labels_its_heuristic(self):
        result = evaluate_system(SimpleBaselineAgent(), load_gold_data()[:3], 'baseline')
        self.assertIn('heuristic_overall_rating', result)
        self.assertNotIn('judge_overall_rating', result)

    def test_heuristic_is_deterministic(self):
        args = ('battery issue', 'Please check Settings > Battery ^AB', '', False, False)
        self.assertEqual(HeuristicReplyRubric.evaluate_reply(*args),
                         HeuristicReplyRubric.evaluate_reply(*args))

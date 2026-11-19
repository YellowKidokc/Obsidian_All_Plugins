"""Known-answer arithmetic fixture; not a review of philosophical truth."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.coherence.cdcm_analyzer import FrameworkMetrics, ConstraintScores


class CDCMFixtureTests(unittest.TestCase):
    def setUp(self):
        self.framework = FrameworkMetrics('known constraints', [
            ConstraintScores('A', 1, 1, 1, 1, 1, 1, 1, 0, 1),
            ConstraintScores('B', 1, 1, 0, 1, 1, 1, 0, 0, 1),
            ConstraintScores('C', 1, 0, 1, 0, 1, 1, 1, -1, 0),
            ConstraintScores('D', 0, 1, 1, 1, 1, 0, 1, 1, 0),
        ])

    def test_known_scores_and_mean(self):
        self.assertEqual(self.framework.net_scores, [8, 6, 4, 6])
        self.assertEqual(self.framework.mean_net_score(), 6)

    def test_coverage_includes_all_nine_distinct_constraints(self):
        self.assertEqual(self.framework.constraint_coverage_ratio(), 1)

    def test_violation_density_is_per_axiom_not_per_cell(self):
        # One violation among four axioms: 0.25, not 1/36 or a percent.
        self.assertEqual(self.framework.violation_density(), 0.25)


if __name__ == '__main__': unittest.main()

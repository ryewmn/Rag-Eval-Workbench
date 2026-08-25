from __future__ import annotations

import math
import unittest

from rag_eval_workbench.metrics import (
    citation_precision,
    ndcg_at_k,
    percentile,
    recall_at_k,
    reciprocal_rank,
)


class MetricsTest(unittest.TestCase):
    def test_recall_at_k(self) -> None:
        self.assertEqual(recall_at_k(["a", "x", "b"], {"a", "b"}, 2), 0.5)

    def test_reciprocal_rank(self) -> None:
        self.assertEqual(reciprocal_rank(["x", "a", "b"], {"a", "b"}, 3), 0.5)

    def test_ndcg_rewards_earlier_relevance(self) -> None:
        early = ndcg_at_k(["a", "x", "b"], {"a", "b"}, 3)
        late = ndcg_at_k(["x", "a", "b"], {"a", "b"}, 3)
        self.assertGreater(early, late)
        self.assertTrue(math.isclose(ndcg_at_k(["a", "b"], {"a", "b"}, 2), 1.0))

    def test_citation_precision(self) -> None:
        self.assertEqual(citation_precision(["a", "x"], {"a"}, 2), 0.5)

    def test_percentile_interpolates(self) -> None:
        self.assertEqual(percentile([0.0, 10.0], 0.95), 9.5)

    def test_percentile_rejects_invalid_quantile(self) -> None:
        with self.assertRaises(ValueError):
            percentile([1.0], 1.1)


if __name__ == "__main__":
    unittest.main()

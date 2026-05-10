import unittest

from rag_pareto.chunking import Chunk
from rag_pareto.data import Query
from rag_pareto.metrics import generation_metrics, retrieval_metrics


class MetricTests(unittest.TestCase):
    def test_retrieval_metrics_hit_at_first_rank(self):
        query = Query("q", "question", ("doc-a",), (), ("alpha",))
        chunks = [Chunk("c1", "doc-a", "A", "alpha beta"), Chunk("c2", "doc-b", "B", "gamma")]
        metrics = retrieval_metrics(query, chunks, k=2)
        self.assertEqual(metrics["recall_at_k"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertGreater(metrics["ndcg_at_k"], 0.99)

    def test_generation_metrics_penalize_unsupported_terms(self):
        query = Query("q", "question", ("doc-a",), (), ("alpha", "omega"))
        chunks = [Chunk("c1", "doc-a", "A", "alpha beta")]
        metrics = generation_metrics(query, "alpha unsupported", chunks)
        self.assertEqual(metrics["context_recall"], 1.0)
        self.assertGreater(metrics["hallucination_risk"], 0.0)


if __name__ == "__main__":
    unittest.main()

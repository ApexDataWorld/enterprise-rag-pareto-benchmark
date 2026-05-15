import unittest

from rag_pareto.embeddings.sentence_transformers_provider import SentenceTransformersProvider


class SentenceTransformersProviderTests(unittest.TestCase):
    def test_missing_dependency_has_clear_message(self):
        try:
            import sentence_transformers  # noqa: F401
        except ModuleNotFoundError:
            with self.assertRaisesRegex(RuntimeError, "optional dependency"):
                SentenceTransformersProvider()
            return
        provider = SentenceTransformersProvider()
        vectors = provider.encode(["enterprise retrieval", "policy search"])
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 384)


if __name__ == "__main__":
    unittest.main()


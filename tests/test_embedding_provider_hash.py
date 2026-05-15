import unittest

from rag_pareto.embeddings import HashEmbeddingProvider


class HashEmbeddingProviderTests(unittest.TestCase):
    def test_hash_embedding_shape_and_stability(self):
        provider = HashEmbeddingProvider(dimensions=96)
        first = provider.encode(["enterprise retrieval"])[0]
        second = provider.encode(["enterprise retrieval"])[0]
        self.assertEqual(len(first), 96)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()


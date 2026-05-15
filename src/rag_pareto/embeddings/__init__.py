"""Embedding providers for retrieval experiments."""

from .hash_provider import HashEmbeddingProvider
from .sentence_transformers_provider import SentenceTransformersProvider

__all__ = ["HashEmbeddingProvider", "SentenceTransformersProvider", "make_embedding_provider"]


def make_embedding_provider(config: dict | None = None):
    config = config or {"type": "dense_hash"}
    provider_type = config.get("type", "dense_hash")
    if provider_type in {"dense_hash", "hash", "deterministic_hash"}:
        return HashEmbeddingProvider(dimensions=int(config.get("embedding_dimension", 96)))
    if provider_type == "sentence_transformers":
        return SentenceTransformersProvider(
            model_name=config.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"),
            normalize=bool(config.get("normalize", True)),
            cache_dir=config.get("cache_dir", ".cache/embeddings"),
        )
    raise ValueError(f"Unsupported embedding provider: {provider_type}")


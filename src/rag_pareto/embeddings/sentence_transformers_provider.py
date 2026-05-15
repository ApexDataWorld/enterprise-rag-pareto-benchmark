"""Optional Sentence Transformers embedding provider."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


class SentenceTransformersProvider:
    expected_dimension = 384

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize: bool = True,
        cache_dir: str = ".cache/embeddings",
    ):
        self.model_name = model_name
        self.normalize = normalize
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Sentence Transformers neural validation requires the optional dependency. "
                "Install it with `python3 -m pip install '.[neural]'` or "
                "`python3 -m pip install sentence-transformers`."
            ) from exc
        self._model = SentenceTransformer(model_name)

    @property
    def name(self) -> str:
        return self.model_name

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        uncached_texts: list[str] = []
        uncached_positions: list[int] = []
        for position, text in enumerate(texts):
            cached = self._read_cache(text)
            if cached is None:
                vectors.append([])
                uncached_texts.append(text)
                uncached_positions.append(position)
            else:
                vectors.append(cached)
        if uncached_texts:
            encoded = self._model.encode(
                uncached_texts,
                normalize_embeddings=self.normalize,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            for position, vector in zip(uncached_positions, encoded):
                values = [float(value) for value in vector.tolist()]
                if len(values) != self.expected_dimension:
                    raise ValueError(
                        f"Expected {self.expected_dimension} dimensions from {self.model_name}, got {len(values)}"
                    )
                vectors[position] = values
                self._write_cache(texts[position], values)
        return vectors

    def _cache_path(self, text: str) -> Path:
        digest = hashlib.sha256(f"{self.model_name}|{self.normalize}|{text}".encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _read_cache(self, text: str) -> list[float] | None:
        path = self._cache_path(text)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_cache(self, text: str, vector: list[float]) -> None:
        self._cache_path(text).write_text(json.dumps(vector), encoding="utf-8")


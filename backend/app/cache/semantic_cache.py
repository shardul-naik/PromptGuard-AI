import json
import hashlib
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb

from backend.app.cache.embeddings import generate_embedding
from backend.app.config import (
    CACHE_RESPONSE_FILE,
    CHROMA_DIR,
    CACHE_SIMILARITY_THRESHOLD,
)


class SemanticCache:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name="promptguard_cache",
            metadata={"hnsw:space": "cosine"},
        )

        self.file_lock = threading.Lock()

        if not CACHE_RESPONSE_FILE.exists():
            CACHE_RESPONSE_FILE.write_text(
                "{}",
                encoding="utf-8",
            )

    def _make_id(self, text: str) -> str:
        normalized = text.strip().lower()

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def _load_responses(self) -> dict[str, Any]:
        with self.file_lock:
            try:
                return json.loads(
                    CACHE_RESPONSE_FILE.read_text(
                        encoding="utf-8"
                    )
                )
            except (json.JSONDecodeError, FileNotFoundError):
                return {}

    def _save_responses(self, data: dict[str, Any]) -> None:
        with self.file_lock:
            CACHE_RESPONSE_FILE.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

    def lookup(self, text: str) -> dict[str, Any] | None:
        embedding = generate_embedding(text)

        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=1,
        )

        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]

        if not ids or not distances:
            return None

        cache_id = ids[0]
        distance = float(distances[0])

        # Chroma cosine distance:
        # similarity ≈ 1 - distance
        similarity = 1.0 - distance

        if similarity < CACHE_SIMILARITY_THRESHOLD:
            return None

        responses = self._load_responses()

        cached = responses.get(cache_id)

        if not cached:
            return None

        return {
            "cache_id": cache_id,
            "similarity": round(similarity, 4),
            "response": cached["response"],
            "metadata": cached.get("metadata", {}),
        }

    def save(
        self,
        text: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:

        embedding = generate_embedding(text)

        cache_id = self._make_id(text)

        self.collection.upsert(
            ids=[cache_id],
            embeddings=[embedding],
            documents=[text],
        )

        responses = self._load_responses()

        responses[cache_id] = {
            "response": response,
            "metadata": metadata or {},
            "saved_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._save_responses(responses)

        return cache_id
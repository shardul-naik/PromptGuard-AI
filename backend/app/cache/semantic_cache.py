import hashlib
import json
import os
import threading
from datetime import datetime, timezone
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

        self.file_lock = threading.RLock()

        if not CACHE_RESPONSE_FILE.exists():
            CACHE_RESPONSE_FILE.write_text(
                "{}",
                encoding="utf-8",
            )

    def _make_id(self, text: str) -> str:
        normalized = " ".join(text.split()).casefold()

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
            temporary_file = CACHE_RESPONSE_FILE.with_suffix(".tmp")
            temporary_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(temporary_file, CACHE_RESPONSE_FILE)

    def lookup(self, text: str) -> dict[str, Any] | None:
        cache_id = self._make_id(text)
        responses = self._load_responses()

        # Exact repeats should hit without loading the embedding model.
        cached = responses.get(cache_id)
        if cached:
            return {
                "cache_id": cache_id,
                "similarity": 1.0,
                "response": cached["response"],
                "metadata": cached.get("metadata", {}),
            }

        with self.file_lock:
            entry_count = self.collection.count()
        if entry_count == 0:
            return None

        embedding = generate_embedding(text)

        with self.file_lock:
            result = self.collection.query(
                query_embeddings=[embedding],
                n_results=min(5, entry_count),
                include=["distances"],
            )

        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]

        # Chroma returns cosine distance; inspect several nearest records in
        # case an older orphaned vector has no matching saved response.
        for candidate_id, distance in zip(ids, distances):
            similarity = 1.0 - float(distance)
            cached = responses.get(candidate_id)
            if cached and similarity >= CACHE_SIMILARITY_THRESHOLD:
                return {
                    "cache_id": candidate_id,
                    "similarity": round(similarity, 4),
                    "response": cached["response"],
                    "metadata": cached.get("metadata", {}),
                }

        return None

    def save(
        self,
        text: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:

        cache_id = self._make_id(text)
        embedding = generate_embedding(text)

        with self.file_lock:
            responses = self._load_responses()
            responses[cache_id] = {
                "response": response,
                "metadata": metadata or {},
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
            self._save_responses(responses)
            self.collection.upsert(
                ids=[cache_id],
                embeddings=[embedding],
                documents=[text],
            )

        return cache_id

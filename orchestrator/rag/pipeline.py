"""
RAG pipeline: store weekly behavioral summaries and retrieve similar ones.
"""

import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings

from mcp_client.models import DayRecord
from rag.embeddings import summarise_week, week_label_for_records

logger = logging.getLogger(__name__)

# Where ChromaDB persists its data on disk
_CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma"
_COLLECTION = "weekly_summaries"


class RAGPipeline:
    """
    Thin wrapper around ChromaDB.
    Main methods:
      store_week()         — upsert this week's summary as an embedding
      find_similar_weeks() — cosine-nearest-neighbour search
    """

    def __init__(self, persist_dir: Path = _CHROMA_DIR) -> None:
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        
        self._col = self._client.get_or_create_collection(
            name=_COLLECTION,
            metadata={"hnsw:space": "cosine"},  
        )
        logger.info(
            "RAGPipeline ready — collection '%s' has %d documents",
            _COLLECTION,
            self._col.count(),
        )

    def store_week(self, user_id: str, records: list[DayRecord]) -> str:
        """
        Embed and upsert a week of DayRecords.
        Returns the week_label used as the document ID (e.g. "2024-W03") for reference.
        """
        week_label = week_label_for_records(records)
        doc_id = f"{user_id}::{week_label}"
        text = summarise_week(records, week_label)

        self._col.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[{"user_id": user_id, "week": week_label}],
        )
        logger.debug("Stored week %s for user %s", week_label, user_id)
        return week_label

    def find_similar_weeks(
        self,
        user_id: str,
        records: list[DayRecord],
        n_results: int = 3,
    ) -> list[dict]:
        """
        Find the n most similar historical weeks for this user.
        Excludes the current week so it's not surfaced as its own match.
        """
        current_week = week_label_for_records(records)
        query_text = summarise_week(records, current_week)

        total_docs = self._col.count()
        if total_docs == 0:
            return []

        # Ask for one extra result to drop the current week if present
        raw = self._col.query(
            query_texts=[query_text],
            n_results=min(n_results + 1, total_docs),
            where={"user_id": user_id},
        )

        results = []
        for i, doc_id in enumerate(raw["ids"][0]):
            week = raw["metadatas"][0][i]["week"]
            if week == current_week:
                continue  # skip self-match

            # ChromaDB returns distances (lower = more similar for cosine)
            # Convert to a 0-1 similarity score: similarity = 1 - distance
            distance = raw["distances"][0][i]
            similarity = round(1.0 - distance, 4)

            results.append(
                {
                    "week": week,
                    "similarity": similarity,
                    "summary": raw["documents"][0][i],
                }
            )

            if len(results) == n_results:
                break

        return results

#!/usr/bin/env python
"""LangChain retriever backed by the MemMachine memories/search endpoint."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import requests
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

logger = logging.getLogger(__name__)


class MemMachineRetriever(BaseRetriever):
    """Retrieve memories from MemMachine for use in LangChain chains."""

    base_url: str = "http://localhost:8080"
    group_id: str = "langchain_examples"
    agent_id: List[str] = ["langchain_agent"]
    user_id: List[str] = ["demo_user"]
    session_id: Optional[str] = None
    limit: int = 10
    timeout: int = 30

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))

    def _make_payload(self, query: str) -> Dict:
        session_block: Dict[str, List[str] | str] = {
            "group_id": self.group_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
        }
        if self.session_id:
            session_block["session_id"] = self.session_id

        return {
            "session": session_block,
            "query": query,
            "limit": self.limit,
            "filter": {},
        }

    def _get_relevant_documents(self, query: str) -> List[Document]:  # type: ignore[override]
        payload = self._make_payload(query)
        try:
            response = requests.post(
                f"{self.base_url}/v1/memories/search",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("MemMachine search failed: %s", exc)
            return []

        content = response.json().get("content", {})
        episodic_memory = content.get("episodic_memory", [])

        documents: List[Document] = []
        for episode in self._flatten(episodic_memory):
            text = episode.get("content") or episode.get("episode_content")
            if not text:
                continue
            metadata = {
                "timestamp": episode.get("timestamp"),
                "episode_type": episode.get("episode_type"),
                "group_id": episode.get("group_id"),
                "session_id": episode.get("session_id"),
                "producer": episode.get("producer_id"),
                "provider": (episode.get("user_metadata") or {}).get("provider"),
            }
            documents.append(Document(page_content=text, metadata=metadata))

        return documents

    def _flatten(self, nested: List) -> List[Dict]:
        flat: List[Dict] = []

        def ingest(item):
            if isinstance(item, dict):
                flat.append(item)
            elif isinstance(item, list):
                for sub in item:
                    ingest(sub)

        ingest(nested)
        return flat

"""LangChain chat history adapter backed by MemMachine episodic memory."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import requests
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class MemMachineChatMessageHistory(BaseChatMessageHistory):
    """Persist chat history to MemMachine's episodic memory API.

    This adapter implements LangChain's ``BaseChatMessageHistory`` interface so that
    MemMachine can be used as the backing store for conversation memory in chains or
    agents. By default it writes every message to the ``/v1/memories/episodic``
    endpoint and keeps a local cache of messages for quick access. Optionally the
    ``load_remote_history`` flag will hydrate the history from MemMachine when the
    class is instantiated.
    """

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:8080",
        group_id: str = "langchain_examples",
        user_id: str = "demo_user",
        agent_id: str = "langchain_agent",
        session_id: str = "langchain_session",
        user_producer: str | None = None,
        agent_producer: str | None = None,
        load_remote_history: bool = False,
        request_timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout

        self._messages: List[BaseMessage] = []
        self._session: Dict[str, List[str] | str] = {
            "group_id": group_id,
            "agent_id": [agent_id],
            "user_id": [user_id],
            "session_id": session_id,
        }

        self.user_producer = user_producer or user_id
        self.agent_producer = agent_producer or agent_id

        if load_remote_history:
            self.pull()

    # ---------------------------------------------------------------------
    # LangChain interface
    # ---------------------------------------------------------------------
    @property
    def messages(self) -> List[BaseMessage]:
        return list(self._messages)

    def add_message(self, message: BaseMessage) -> None:
        self._messages.append(message)
        self._persist_message(message)

    def add_user_message(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("User message must be a string")
        self.add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("AI message must be a string")
        self.add_message(AIMessage(content=message))

    def clear(self) -> None:
        self._messages.clear()
        payload = {"session": self._session}
        try:
            requests.post(
                f"{self.base_url}/v1/memories/episodic/clear",
                json=payload,
                timeout=self.request_timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - best effort
            logger.debug("Unable to clear episodic memory: %s", exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def pull(self, limit: int = 50) -> None:
        """Hydrate local history from MemMachine search results."""

        payload = {
            "session": self._session,
            "query": "Recent conversation context",
            "limit": limit,
            "filter": {},
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/memories/search",
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            content = response.json().get("content", {})
            episodic_memory = content.get("episodic_memory", [])
        except requests.RequestException as exc:
            logger.warning("Failed to pull history from MemMachine: %s", exc)
            return

        messages: List[BaseMessage] = []
        for episode in self._flatten_episodes(episodic_memory):
            msg = self._episode_to_message(episode)
            if msg:
                messages.append(msg)

        # MemMachine returns newest first; reverse to chronological order
        messages.reverse()
        self._messages = messages

    def get_recent_messages(self, limit: int = 5, refresh: bool = False) -> List[BaseMessage]:
        """Return the most recent messages, optionally refreshing from MemMachine."""

        if refresh:
            self.pull(limit=limit)

        if limit <= 0:
            return []

        return list(self._messages[-limit:])

    # ------------------------------------------------------------------
    def _persist_message(self, message: BaseMessage) -> None:
        episode_content = message.content
        if isinstance(episode_content, (list, tuple)):
            episode_content = "\n".join(str(part) for part in episode_content)

        metadata = {
            "message_type": message.type,
            "provider": "langchain",
        }

        producer = self.user_producer if message.type == "human" else self.agent_producer
        produced_for = self.agent_producer if producer == self.user_producer else self.user_producer

        payload = {
            "session": self._session,
            "producer": producer,
            "produced_for": produced_for,
            "episode_content": episode_content,
            "episode_type": f"langchain_{message.type}",
            "metadata": metadata,
        }

        try:
            requests.post(
                f"{self.base_url}/v1/memories/episodic",
                json=payload,
                timeout=self.request_timeout,
            ).raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Failed to persist message to MemMachine: %s", exc)

    # ------------------------------------------------------------------
    @staticmethod
    def _flatten_episodes(raw_episodes: List) -> List[Dict]:
        flat: List[Dict] = []

        def _ingest(item: Optional[Dict]) -> None:
            if not item or not isinstance(item, dict):
                return
            flat.append(item)

        for entry in raw_episodes:
            if isinstance(entry, list):
                for sub in entry:
                    _ingest(sub)
            else:
                _ingest(entry)
        return flat

    def _episode_to_message(self, episode: Dict) -> Optional[BaseMessage]:
        content = episode.get("content") or episode.get("episode_content")
        if not content:
            return None

        metadata = episode.get("metadata") or episode.get("user_metadata") or {}
        role = metadata.get("message_type") or metadata.get("role") or episode.get("episode_type")

        if role and "human" in role:
            return HumanMessage(content=content)
        if role and ("assistant" in role or "ai" in role):
            return AIMessage(content=content)
        if role and "system" in role:
            return SystemMessage(content=content)

        # Default heuristic based on producer metadata
        producer = episode.get("producer") or metadata.get("producer")
        if producer == self.user_producer:
            return HumanMessage(content=content)
        if producer == self.agent_producer:
            return AIMessage(content=content)

        return HumanMessage(content=content)



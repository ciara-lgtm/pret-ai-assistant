from __future__ import annotations

from typing import Protocol

from app.models.chat import KnowledgeChunk


class Retriever(Protocol):
    """Provider-independent interface for retrieving relevant knowledge snippets."""

    def retrieve(self, query: str) -> list[KnowledgeChunk]:
        """Return the most relevant knowledge chunks for the supplied user query."""
        ...

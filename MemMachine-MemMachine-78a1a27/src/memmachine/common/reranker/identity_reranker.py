"""
Identity reranker implementation.
"""

from .reranker import Reranker


class IdentityReranker(Reranker):
    """
    Reranker that returns candidates in their original order
    without any reordering.
    """

    async def score(self, query: str, candidates: list[str]) -> list[float]:
        scores = list(map(float, reversed(range(len(candidates)))))
        return scores

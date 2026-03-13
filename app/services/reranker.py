"""Cross-Encoder re-ranking via sentence-transformers."""
import logging
from functools import lru_cache

from app.core.config import get_settings
from app.models.search import ConfluencePage

logger = logging.getLogger(__name__)


class Reranker:
    def __init__(self) -> None:
        settings = get_settings()
        logger.info("Loading re-ranker model: %s", settings.reranker_model)
        from sentence_transformers import CrossEncoder  # lazy import

        self._model = CrossEncoder(settings.reranker_model)
        logger.info("Re-ranker ready.")

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def rerank(self, query: str, pages: list[ConfluencePage], top_k: int) -> list[ConfluencePage]:
        if not pages:
            return []

        pairs = [(query, f"{p.title}. {p.excerpt}") for p in pages]
        scores: list[float] = self._model.predict(pairs).tolist()

        scored = sorted(zip(scores, pages), key=lambda x: x[0], reverse=True)
        results = []
        for score, page in scored[:top_k]:
            page.score = round(score, 4)
            results.append(page)
        return results


@lru_cache(maxsize=1)
def get_reranker() -> Reranker:
    return Reranker()

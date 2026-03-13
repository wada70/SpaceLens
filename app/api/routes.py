import time
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.core.config import Settings, get_settings
from app.models.health import HealthResponse
from app.models.search import SearchRequest, SearchResponse
from app.services.confluence import get_confluence_client
from app.services.keyword_extractor import extract_keywords, keywords_to_cql
from app.services.reranker import get_reranker
from app.services.answer_synthesizer import synthesize_answer

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["ops"])
async def health():
    confluence = get_confluence_client()
    reranker = get_reranker()
    return HealthResponse(
        status="ok",
        confluence_reachable=await confluence.health_check(),
        reranker_loaded=reranker.loaded,
    )


# ── Search ────────────────────────────────────────────────────────────────────

@router.post("/search", response_model=SearchResponse, tags=["search"])
async def search(
    req: SearchRequest,
    settings: Settings = Depends(get_settings),
):
    t0 = time.monotonic()

    # 1. Extract keywords
    keywords = await extract_keywords(req.query)

    # 2. Build CQL and query Confluence
    space_keys = req.space_keys or settings.confluence_space_keys or None
    cql = keywords_to_cql(keywords, space_keys)
    logger.info("CQL: %s", cql)

    confluence = get_confluence_client()
    raw_pages = await confluence.search(cql, limit=settings.search_max_results)

    if not raw_pages:
        return SearchResponse(
            query=req.query,
            keywords=keywords,
            answer="No relevant Confluence pages were found for your question.",
            results=[],
            duration_ms=round((time.monotonic() - t0) * 1000, 1),
        )

    # 3. Re-rank
    reranker = get_reranker()
    top_pages = reranker.rerank(req.query, raw_pages, top_k=req.top_k)

    # 4. Synthesize answer
    answer = await synthesize_answer(req.query, top_pages[:3])

    return SearchResponse(
        query=req.query,
        keywords=keywords,
        answer=answer,
        results=top_pages,
        duration_ms=round((time.monotonic() - t0) * 1000, 1),
    )

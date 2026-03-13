"""Confluence Data Center search & page-fetch service."""
import logging
from functools import lru_cache

import httpx

from app.core.config import get_settings
from app.models.search import ConfluencePage

logger = logging.getLogger(__name__)


class ConfluenceClient:
    """Thin async wrapper around the Confluence REST API v1."""

    def __init__(self) -> None:
        s = get_settings()
        self._base = s.confluence_url.rstrip("/")

        if s.confluence_pat:
            auth_headers = {"Authorization": f"Bearer {s.confluence_pat}"}
            auth = None
        else:
            auth_headers = {}
            auth = (s.confluence_username, s.confluence_api_token)

        self._client = httpx.AsyncClient(
            base_url=self._base,
            auth=auth,
            timeout=30,
            headers={"Accept": "application/json", **auth_headers},
        )

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get("/rest/api/space", params={"limit": 1})
            return resp.status_code == 200
        except Exception:
            return False

    async def search(
        self,
        cql: str,
        limit: int = 20,
    ) -> list[ConfluencePage]:
        """Execute a CQL query and return lightweight page objects."""
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "space,history.lastUpdated,excerpt",
        }
        try:
            resp = await self._client.get("/rest/api/search", params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("Confluence search failed: %s", exc)
            return []

        pages: list[ConfluencePage] = []
        for item in resp.json().get("results", []):
            pages.append(
                ConfluencePage(
                    id=item["id"],
                    title=item["title"],
                    url=f"{self._base}/pages/viewpage.action?pageId={item['id']}",
                    space_key=item.get("space", {}).get("key", ""),
                    space_name=item.get("space", {}).get("name", ""),
                    excerpt=item.get("excerpt", ""),
                    last_modified=(
                        item.get("history", {})
                        .get("lastUpdated", {})
                        .get("when", "")
                    ),
                )
            )
        return pages

    async def get_page_body(self, page_id: str) -> str:
        """Return the plain-text body of a single page."""
        try:
            resp = await self._client.get(
                f"/rest/api/content/{page_id}",
                params={"expand": "body.export_view"},
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.warning("Could not fetch page %s: %s", page_id, exc)
            return ""

        raw_html = resp.json().get("body", {}).get("export_view", {}).get("value", "")
        return _strip_html(raw_html)

    async def aclose(self) -> None:
        await self._client.aclose()


def _strip_html(html: str) -> str:
    """Very lightweight HTML→plain-text (no extra deps)."""
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


@lru_cache(maxsize=1)
def get_confluence_client() -> ConfluenceClient:
    return ConfluenceClient()

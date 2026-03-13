from pydantic import BaseModel, HttpUrl, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural-language question")
    space_keys: list[str] | None = Field(None, description="Confluence space keys to limit search")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


class ConfluencePage(BaseModel):
    id: str
    title: str
    url: HttpUrl
    space_key: str
    space_name: str
    excerpt: str = ""
    last_modified: str = ""
    score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    keywords: list[str]
    answer: str
    results: list[ConfluencePage]
    duration_ms: float

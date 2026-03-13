from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    confluence_reachable: bool
    reranker_loaded: bool
    version: str = "0.1.0"

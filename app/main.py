from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
import pathlib

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.routes import router

setup_logging()

settings = get_settings()
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the re-ranker model on startup so first query isn't slow
    from app.services.reranker import get_reranker
    get_reranker()
    yield
    # Cleanup
    from app.services.confluence import get_confluence_client
    await get_confluence_client().aclose()


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": settings.app_title})

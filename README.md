# SpaceLens

> AI-powered semantic search for Confluence Data Center

SpaceLens turns natural-language questions into effective Confluence searches, re-ranks results for relevance, reads the most relevant pages, and returns a concise AI-generated answer with source links — all without a vector database.

## Architecture

```
Browser / Bookmarklet
      │
      ▼
FastAPI  (/api/search)
  │
  ├─ 1. LLM keyword extraction   (Anthropic Claude Haiku)
  ├─ 2. Confluence CQL search    (REST API)
  ├─ 3. Cross-Encoder re-ranking (sentence-transformers)
  ├─ 4. Full page fetch          (top-3 pages)
  └─ 5. Answer synthesis         (Anthropic Claude Haiku)
```

## Quick start

### Local (Python)

```bash
# 1. Copy and fill in secrets
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pre-download the re-ranker model (optional but recommended)
python scripts/download_model.py

# 4. Start the server
uvicorn app.main:app --reload
# → http://localhost:8000
```

### Docker

```bash
cp .env.example .env   # fill in your credentials
docker compose up --build
# → http://localhost:8000
```

## Configuration

All settings are read from environment variables (or `.env`).
See [`.env.example`](.env.example) for the full list.

| Variable | Default | Description |
|---|---|---|
| `CONFLUENCE_URL` | — | Base URL of your Confluence instance |
| `CONFLUENCE_USERNAME` | — | Username / email |
| `CONFLUENCE_API_TOKEN` | — | Personal access token |
| `CONFLUENCE_SPACE_KEYS` | `[]` | JSON array of space keys to limit search, e.g. `["ENG","HR"]` |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `LLM_MODEL` | `claude-haiku-4-5-20251001` | Model used for keyword extraction & answer synthesis |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | HuggingFace Cross-Encoder model |
| `RERANKER_TOP_K` | `5` | Pages kept after re-ranking |
| `SEARCH_MAX_RESULTS` | `20` | Raw results fetched from Confluence |

## Bookmarklet

Open SpaceLens in your browser and drag the **🔭 SpaceLens Search** button to your bookmarks bar.
Clicking it on any Confluence page will open SpaceLens with the page title pre-filled as a query.

An embeddable floating-widget snippet is also available in the UI.

## API

Interactive docs at `http://localhost:8000/docs`.

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Liveness + dependency check |
| `/api/search` | POST | Semantic search + answer |

### Search request

```json
{
  "query": "What is our on-call rotation policy?",
  "space_keys": ["ENG"],
  "top_k": 5
}
```

## Development

```bash
# Run tests
pytest

# Lint
ruff check .
```

## License

MIT

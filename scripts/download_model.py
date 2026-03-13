#!/usr/bin/env python3
"""
Pre-download the re-ranker model so the first request isn't slow.
Run once after installing requirements:
    python scripts/download_model.py
"""
from app.core.config import get_settings
from sentence_transformers import CrossEncoder

settings = get_settings()
print(f"Downloading model: {settings.reranker_model}")
CrossEncoder(settings.reranker_model)
print("Done. Model cached in ~/.cache/huggingface/")

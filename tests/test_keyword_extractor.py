"""Unit tests for keyword extraction helpers (no LLM calls)."""
import pytest
from app.services.keyword_extractor import keywords_to_cql


def test_keywords_to_cql_no_spaces():
    cql = keywords_to_cql(["on-call", "rotation", "policy"])
    assert 'text ~ "on-call"' in cql
    assert "ORDER BY lastmodified DESC" in cql
    assert "space IN" not in cql


def test_keywords_to_cql_with_spaces():
    cql = keywords_to_cql(["deployment"], space_keys=["ENG", "OPS"])
    assert 'space IN ("ENG", "OPS")' in cql


def test_keywords_to_cql_single_keyword():
    cql = keywords_to_cql(["kubernetes"])
    assert "type = page" in cql
    assert 'text ~ "kubernetes"' in cql

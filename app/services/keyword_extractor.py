"""Use the LLM to turn a natural-language question into Confluence CQL keywords."""
import logging
import re

import anthropic

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a search query optimizer for Confluence Data Center.
Given a natural-language question, extract 3–6 highly relevant search keywords or short phrases.
Output ONLY a JSON array of strings, nothing else. Example: ["keyword1", "phrase two", "keyword3"]
"""


async def extract_keywords(question: str) -> list[str]:
    """Return a list of CQL-friendly keywords for the given question."""
    settings = get_settings()
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        message = await client.messages.create(
            model=settings.llm_model,
            max_tokens=128,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        raw = message.content[0].text.strip()
        keywords: list[str] = _parse_json_array(raw)
        logger.debug("Extracted keywords: %s", keywords)
        return keywords
    except Exception as exc:
        logger.warning("Keyword extraction failed, falling back to raw query: %s", exc)
        return [question]


def _parse_json_array(text: str) -> list[str]:
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return [text]
    import json
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return [text]


def keywords_to_cql(keywords: list[str], space_keys: list[str] | None = None) -> str:
    """Build a simple CQL query from a list of keywords."""
    terms = " OR ".join(f'text ~ "{kw}"' for kw in keywords)
    cql = f"type = page AND ({terms})"
    if space_keys:
        spaces = ", ".join(f'"{sk}"' for sk in space_keys)
        cql += f" AND space IN ({spaces})"
    cql += " ORDER BY lastmodified DESC"
    return cql

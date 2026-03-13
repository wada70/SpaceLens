"""Generate a concise answer from the top-ranked Confluence pages."""
import logging

import anthropic

from app.core.config import get_settings
from app.models.search import ConfluencePage
from app.services.confluence import get_confluence_client

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a helpful enterprise knowledge assistant.
Answer the user's question concisely (2–4 sentences) using ONLY the provided Confluence page excerpts.
If the excerpts do not contain enough information to answer, say so honestly.
Do not invent facts. Cite page titles inline when helpful.
"""


async def synthesize_answer(
    question: str,
    pages: list[ConfluencePage],
    fetch_full_body: bool = True,
) -> str:
    settings = get_settings()
    confluence = get_confluence_client()

    context_parts: list[str] = []
    for page in pages:
        if fetch_full_body:
            body = await confluence.get_page_body(page.id)
            # Truncate to ~2000 chars per page to stay within token budget
            snippet = body[:2000] if body else page.excerpt
        else:
            snippet = page.excerpt
        context_parts.append(f"### {page.title}\n{snippet}")

    context = "\n\n".join(context_parts)
    user_message = f"Question: {question}\n\nContext from Confluence:\n{context}"

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        message = await client.messages.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text.strip()
    except Exception as exc:
        logger.error("Answer synthesis failed: %s", exc)
        return "Unable to generate an answer at this time."

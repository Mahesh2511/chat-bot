import logging
import re
from functools import lru_cache

from langchain_core.messages import AIMessage, HumanMessage

from utils.llm_adapter import get_llm

logger = logging.getLogger(__name__)


@lru_cache
def _get_chat():
    return get_llm(temperature=0, max_tokens=512)


def _response_language(question: str) -> str:
    """
    Detect language with Python — never leaves it to LLM guessing.
    Arabic Unicode block: U+0600–U+06FF
    Rule: any Arabic characters present (even mixed) → Arabic, else English.
    """
    return "Arabic" if re.search(r'[؀-ۿ]', question) else "English"


def generate_answer(state):
    summary = state.get("summary", "")
    messages = state.get("messages") or []
    docs = state.get("docs", "")
    question = state["question"]
    lang = _response_language(question)

    recent = messages[-6:]
    history = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in recent
    )

    prompt = f"""You are a helpful assistant.

Conversation Summary:
{summary}

Recent Chat:
{history}

Relevant Context:
{docs}

User Question:
{question}

Rules:
- Answer ONLY from the context above if possible.
- Be concise (2-3 sentences max).
- Do not repeat history.
- YOU MUST respond in {lang} only. No exceptions.
  (Pure English question → English. Any Arabic characters present, even mixed → Arabic.)
"""

    response = _get_chat().invoke(prompt)
    logger.debug("Generated answer for user %s (lang=%s)", state.get("user_id"), lang)

    return {
        "messages": messages + [
            HumanMessage(content=question),
            AIMessage(content=response.content),
        ]
    }

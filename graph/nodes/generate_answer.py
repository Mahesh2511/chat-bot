import logging
import re
from functools import lru_cache

from langchain_core.messages import AIMessage, HumanMessage

from prompts.answer import build_answer_prompt
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

    prompt = build_answer_prompt(
        summary=summary,
        history=history,
        docs=docs,
        question=question,
        lang=lang,
    )

    response = _get_chat().invoke(prompt)
    logger.info("Generated answer for user %s (lang=%s)", state.get("user_id"), lang)

    return {
        "messages": messages + [
            HumanMessage(content=question),
            AIMessage(content=response.content),
        ]
    }

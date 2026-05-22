import logging
import re
from functools import lru_cache

from langchain_core.messages import HumanMessage

from utils.llm_adapter import get_llm

logger = logging.getLogger(__name__)


@lru_cache
def _get_chat():
    return get_llm(temperature=0, max_tokens=256)


def _summary_language(messages: list) -> str:
    """Use Arabic if any user message contains Arabic characters, else English."""
    user_text = " ".join(
        m.content for m in messages if isinstance(m, HumanMessage)
    )
    return "Arabic" if re.search(r'[؀-ۿ]', user_text) else "English"


def summarize(state):
    messages = state.get("messages") or []

    if len(messages) < 4:
        return state

    lang = _summary_language(messages)
    text = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in messages
    )

    summary = _get_chat().invoke(f"""Summarize this conversation in max 4 lines.
Focus only on: user intent, key questions, important answers.
YOU MUST write the summary in {lang} only. No exceptions.

Conversation:
{text}
""")

    logger.debug("Summarized conversation (%d messages, lang=%s)", len(messages), lang)

    return {
        **state,
        "summary": summary.content,
        "messages": messages[-6:],
    }

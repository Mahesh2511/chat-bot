import logging

from db.vector import get_vectorstore

logger = logging.getLogger(__name__)


def retrieve_context(state):
    docs = get_vectorstore().similarity_search(state["question"], k=3)
    context = "\n\n".join(d.page_content for d in docs)
    logger.info("Retrieved %d docs for query", len(docs))
    return {"docs": context}

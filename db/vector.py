from functools import lru_cache

import chromadb
from langchain_chroma import Chroma

from config import get_settings
from utils.embedding_adapter import get_embeddings


@lru_cache
def get_vectorstore() -> Chroma:
    setting = get_settings()
    client = chromadb.PersistentClient(path=setting.chroma_persist_dir)
    return Chroma(
        client=client,
        collection_name=setting.chroma_collection,
        embedding_function=get_embeddings(),
    )


# backward-compatible alias
def chroma() -> Chroma:
    return get_vectorstore()

from functools import lru_cache

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

from app.config import config


@lru_cache(maxsize=1)
def get_retriever():
    Settings.embed_model = OpenAIEmbedding(
        model=config.embedding_model,
    )

    vector_store = FaissVectorStore.from_persist_dir(config.storage_dir)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=config.storage_dir
    )
    index = load_index_from_storage(storage_context=storage_context)

    return index.as_retriever(similarity_top_k=config.similarity_top_k)


def retrieve(query: str) -> list[dict]:
    retriever = get_retriever()
    nodes = retriever.retrieve(query)

    results = []
    for node in nodes:
        content = node.node.get_content().strip()
        # The indexer uses "title" and "url" metadata keys
        title = node.node.metadata.get("title")
        source = title if title else " ".join(content.split()[:5]) + "..."
        results.append({"content": content, "source": source})
    
    return results


from functools import lru_cache

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.config import config


@lru_cache(maxsize=1)
def get_retriever():
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=config.embedding_model,
    )

    storage_context = StorageContext.from_defaults(persist_dir=config.storage_dir)
    index = load_index_from_storage(storage_context)

    return index.as_retriever(similarity_top_k=config.similarity_top_k)


def retrieve(query: str) -> list[str]:
    retriever = get_retriever()
    nodes = retriever.retrieve(query)

    return [
        " ".join(node.node.get_content().split())
        for node in nodes
    ]

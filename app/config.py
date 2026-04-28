import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw_value!r}") from exc


@dataclass(frozen=True)
class RagConfig:
    data_dir: str = os.getenv("RAG_DATA_DIR", "data")
    storage_dir: str = os.getenv("RAG_STORAGE_DIR", "storage")
    embedding_model: str = os.getenv(
        "RAG_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    llm_model: str = os.getenv("RAG_LLM_MODEL", "llama3.2:3b")
    chunk_size: int = _get_int("RAG_CHUNK_SIZE", 1024)
    chunk_overlap: int = _get_int("RAG_CHUNK_OVERLAP", 200)
    similarity_top_k: int = _get_int("RAG_SIMILARITY_TOP_K", 3)


config = RagConfig()

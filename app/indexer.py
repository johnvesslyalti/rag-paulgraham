import json
from pathlib import Path
import faiss
from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

from app.config import config

Settings.embed_model = OpenAIEmbedding(
    model=config.embedding_model,
)
Settings.chunk_size = config.chunk_size
Settings.chunk_overlap = config.chunk_overlap

def build_index():
    # text-embedding-3-small output dimension is 1536
    d = 1536
    faiss_index = faiss.IndexFlatL2(d)
    
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Correctly parse the JSON file instead of reading raw JSON syntax
    json_path = Path(config.data_dir) / "articles.json"
    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    documents = [
        Document(
            text=article["content"], 
            metadata={"title": article["title"], "url": article["url"]}
        )
        for article in articles
    ]

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    index.storage_context.persist(persist_dir=config.storage_dir)

    print("✅ FAISS Index created locally (with proper JSON parsing)")


if __name__ == "__main__":
    build_index()


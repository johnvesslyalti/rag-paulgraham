from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.config import config

Settings.embed_model = HuggingFaceEmbedding(
    model_name=config.embedding_model,
)
Settings.chunk_size = config.chunk_size
Settings.chunk_overlap = config.chunk_overlap

def build_index():
    documents = SimpleDirectoryReader(config.data_dir).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=config.storage_dir)

    print("✅ Index created locally")


if __name__ == "__main__":
    build_index()

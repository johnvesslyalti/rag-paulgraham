from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def query_rag():
    # Set the same embedding model used during indexing
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    storage_context = StorageContext.from_defaults(persist_dir="storage")
    index = load_index_from_storage(storage_context)

    # Setup local LLM with an increased timeout for local generation
    llm = Ollama(model="llama3", request_timeout=360.0)

    # Better prompt (IMPORTANT)
    qa_prompt = PromptTemplate(
        "You are answering based ONLY on the provided context.\n"
        "Do not add extra information.\n\n"
        "Context:\n{context_str}\n\n"
        "Question:\n{query_str}\n\n"
        "Answer:"
    )

    query_engine = index.as_query_engine(llm=llm, text_qa_template=qa_prompt)

    while True:
        query = input("\nAsk something (or type 'exit'): ")
        if query.lower() == "exit":
            break

        response = query_engine.query(query)
        print("\n💬 Answer:", response)


if __name__ == "__main__":
    query_rag()
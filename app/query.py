import sys
import threading
import time

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.config import config


def _format_elapsed(seconds: float) -> str:
    minutes, remaining_seconds = divmod(int(seconds), 60)
    if minutes:
        return f"{minutes}m {remaining_seconds:02d}s"
    return f"{remaining_seconds}s"


def _run_with_wait_timer(message, work):
    done = threading.Event()
    result = {}

    def show_wait_time():
        start_time = time.monotonic()
        while not done.wait(1):
            elapsed = _format_elapsed(time.monotonic() - start_time)
            sys.stdout.write(f"\r{message} ({elapsed})")
            sys.stdout.flush()

    timer_thread = threading.Thread(target=show_wait_time, daemon=True)
    timer_thread.start()

    start_time = time.monotonic()
    try:
        result["value"] = work()
    except Exception as exc:
        result["error"] = exc
    finally:
        done.set()
        elapsed = _format_elapsed(time.monotonic() - start_time)
        sys.stdout.write(f"\r{message} ({elapsed})\n")
        sys.stdout.flush()

    if "error" in result:
        raise result["error"]

    return result["value"]


def query_rag():
    # Set the same embedding model used during indexing
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=config.embedding_model,
    )

    storage_context = StorageContext.from_defaults(persist_dir=config.storage_dir)
    index = load_index_from_storage(storage_context)

    # Setup local LLM with an increased timeout for local generation
    llm = Ollama(
        model=config.llm_model,
        request_timeout=360.0,
        temperature=0,
        additional_kwargs={"options": {"num_predict": 180}},
    )

    qa_prompt = PromptTemplate(
        "You are a careful reading assistant.\n"
        "Answer using ONLY the provided context.\n"
        "Follow the user's requested format exactly. If the user asks for a specific "
        "number of points, provide exactly that many points.\n"
        "If the question is broad or vague, summarize the essay's main thesis first, "
        "then mention 2-4 supporting points.\n"
        "If the context does not contain enough information, say that the essay does "
        "not provide enough context to answer.\n"
        "Do not add facts from outside the context.\n\n"
        "Keep the answer under 150 words.\n\n"
        "Context:\n{context_str}\n\n"
        "Question:\n{query_str}\n\n"
        "Answer:"
    )

    query_engine = index.as_query_engine(
        llm=llm,
        text_qa_template=qa_prompt,
        similarity_top_k=config.similarity_top_k,
    )

    while True:
        query = input("\nAsk something (or type 'exit'): ")
        if query.lower() == "exit":
            break

        response = _run_with_wait_timer(
            "Waiting for Ollama to answer",
            lambda: query_engine.query(query),
        )
        print("\n💬 Answer:", response)

        if response.source_nodes:
            print("\n📚 Sources:")
            for index, source_node in enumerate(response.source_nodes, start=1):
                snippet = " ".join(source_node.node.get_content().split())
                print(f"{index}. {snippet[:300]}...")


if __name__ == "__main__":
    query_rag()

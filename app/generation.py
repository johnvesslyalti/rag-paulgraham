from functools import lru_cache

from llama_index.llms.ollama import Ollama

from app.config import config


@lru_cache(maxsize=1)
def get_llm():
    return Ollama(
        model=config.llm_model,
        request_timeout=360.0,
        temperature=0,
        additional_kwargs={"options": {"num_predict": 180}},
    )


def generate_answer(query: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)
    prompt = (
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
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\n"
        "Answer:"
    )

    response = get_llm().complete(prompt)
    return str(response)

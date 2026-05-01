import json
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


def get_json_llm():
    return Ollama(
        model=config.llm_model,
        request_timeout=360.0,
        temperature=0,
        additional_kwargs={"options": {"num_predict": 300}},
        format="json"
    )


def generate_answer(query: str, chunks: list[str]) -> tuple[str, list[str]]:
    context = "\n\n".join(chunks)
    prompt = (
        "You are a careful reading assistant.\n"
        "Answer using ONLY the provided context. If a piece of the context seems "
        "irrelevant to the specific topic or essay being asked about, IGNORE IT.\n"
        "Follow the user's requested format exactly. If the user asks for a specific "
        "number of points, provide exactly that many points.\n"
        "If the question is broad or vague, summarize the essay's main thesis first, "
        "then mention 2-4 supporting points.\n"
        "If the context does not contain enough information, say that the essay does "
        "not provide enough context to answer.\n"
        "Do not add facts from outside the context.\n\n"
        "Keep the answer under 150 words.\n\n"
        "ALSO, provide 2-3 follow-up questions based on the context and your answer.\n"
        "Output the result ONLY as a JSON object with two keys: \"answer\" (string) and \"suggested_questions\" (list of strings).\n"
        "Do NOT wrap the JSON in markdown blocks.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\n"
    )

    response = get_json_llm().complete(prompt)
    try:
        data = json.loads(str(response))
        answer = data.get("answer", str(response))
        suggested = data.get("suggested_questions", [])
        return answer, suggested
    except Exception:
        return str(response), []


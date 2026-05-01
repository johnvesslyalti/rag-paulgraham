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


async def generate_answer_stream(query: str, chunks: list[str]):
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
        "IMPORTANT: After your answer, you MUST write exactly '---SUGGESTED_QUESTIONS---' on a new line, "
        "followed by 2-3 follow-up questions related to the context. Each question MUST be on a new line and start with a dash (-).\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\n"
        "Answer:"
    )

    llm = get_llm()
    response_gen = await llm.astream_complete(prompt)
    
    in_questions_section = False
    accumulated_questions_text = ""
    accumulated_buffer = ""
    marker = "---SUGGESTED_QUESTIONS---"

    async for chunk in response_gen:
        delta = chunk.delta
        if not in_questions_section:
            accumulated_buffer += delta
            if marker in accumulated_buffer:
                in_questions_section = True
                parts = accumulated_buffer.split(marker)
                if parts[0]:
                    yield json.dumps({"type": "chunk", "content": parts[0]}) + "\n"
                if len(parts) > 1:
                    accumulated_questions_text += parts[1]
            else:
                if len(accumulated_buffer) > len(marker):
                    safe_to_yield = accumulated_buffer[:-len(marker)]
                    accumulated_buffer = accumulated_buffer[-len(marker):]
                    if safe_to_yield:
                        yield json.dumps({"type": "chunk", "content": safe_to_yield}) + "\n"
        else:
            accumulated_questions_text += delta

    if not in_questions_section:
        if accumulated_buffer:
            yield json.dumps({"type": "chunk", "content": accumulated_buffer}) + "\n"
    else:
        questions = [q.strip().lstrip("-").strip() for q in accumulated_questions_text.split("\n") if q.strip().startswith("-")]
        yield json.dumps({"type": "suggested_questions", "content": questions}) + "\n"



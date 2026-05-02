import json
from functools import lru_cache

from llama_index.llms.openai import OpenAI

from app.config import config


@lru_cache(maxsize=1)
def get_llm():
    return OpenAI(
        model=config.llm_model,
        temperature=0,
        max_tokens=180,
    )


@lru_cache(maxsize=1)
def get_rewriter_llm():
    return OpenAI(
        model=config.llm_model,
        temperature=0,
        max_tokens=50, # Rewriting needs very few tokens
    )


def get_json_llm():
    return OpenAI(
        model=config.llm_model,
        temperature=0,
        max_tokens=300,
    )


async def generate_answer_stream(query: str, chunks: list[str]):
    context = "\n\n".join(chunks)
    prompt = (
        "You are an AI assistant answering questions strictly based on the provided context.\n\n"
        "Rules:\n"
        "- Use ONLY the provided context to answer\n"
        "- Do NOT use outside knowledge\n"
        "- If the answer is not in the context, say:\n"
        "  \"I don't know based on the provided documents\"\n"
        "- Be concise and accurate\n"
        "- Do NOT make assumptions\n\n"
        "IMPORTANT: After your answer, you MUST write exactly '---SUGGESTED_QUESTIONS---' on a new line, "
        "followed by 2-3 follow-up questions related to the context. Each question MUST be on a new line and start with a dash (-).\n\n"
        f"Context:\n{context}\n\n"
        "Answer ONLY from the above context.\n\n"
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



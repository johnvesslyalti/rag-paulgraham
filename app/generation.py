import json
from functools import lru_cache

from llama_index.llms.openai import OpenAI

from app.config import config


@lru_cache(maxsize=1)
def get_llm():
    return OpenAI(
        model=config.llm_model,
        temperature=0.2,
        max_tokens=500,
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


async def generate_answer_stream(query: str, chunks: list[str], sources: list[str] = None):
    context = "\n\n".join(chunks)
    refusal_phrase = "I don't know based on the provided documents"
    prompt = (
        "You are an AI assistant answering questions strictly based on the provided context.\n\n"
        "Rules:\n"
        "- Use ONLY the provided context to answer\n"
        "- Do NOT use outside knowledge\n"
        "- If the answer is not in the context, say:\n"
        f"  \"{refusal_phrase}\"\n"
        "- Even if you don't know the answer, you MUST still provide 2-3 follow-up questions about the provided context to help the user learn about what IS in the documents.\n"
        "- If you DO have an answer, be concise and accurate.\n\n"
        f"Context:\n{context}\n\n"
        "Answer ONLY from the above context.\n\n"
        f"Question:\n{query}\n\n"
        "Answer:\n\n"
        "IMPORTANT: After your answer, you MUST write exactly '---SUGGESTED_QUESTIONS---' on a new line, "
        "followed by 2-3 follow-up questions related to the context (or related to what the user COULD ask about this context). Each question MUST be on a new line and start with a dash (-)."
    )

    llm = get_llm()
    response_gen = await llm.astream_complete(prompt)
    
    in_questions_section = False
    accumulated_questions_text = ""
    accumulated_buffer = ""
    full_answer_content = ""
    marker = "---SUGGESTED_QUESTIONS---"

    async for chunk in response_gen:
        delta = chunk.delta
        if not in_questions_section:
            accumulated_buffer += delta
            if marker in accumulated_buffer:
                in_questions_section = True
                parts = accumulated_buffer.split(marker)
                if parts[0]:
                    full_answer_content += parts[0]
                    yield json.dumps({"type": "chunk", "content": parts[0]}) + "\n"
                if len(parts) > 1:
                    accumulated_questions_text += parts[1]
            else:
                if len(accumulated_buffer) > len(marker):
                    safe_to_yield = accumulated_buffer[:-len(marker)]
                    accumulated_buffer = accumulated_buffer[-len(marker):]
                    if safe_to_yield:
                        full_answer_content += safe_to_yield
                        yield json.dumps({"type": "chunk", "content": safe_to_yield}) + "\n"
        else:
            accumulated_questions_text += delta

    if not in_questions_section:
        if accumulated_buffer:
            full_answer_content += accumulated_buffer
            yield json.dumps({"type": "chunk", "content": accumulated_buffer}) + "\n"
    
    # Check for refusal
    answer_lower = full_answer_content.lower()
    refusal_keywords = [
        refusal_phrase.lower(),
        "i don't know",
        "not mentioned in the context",
        "not provided in the context",
        "does not contain information",
        "not in the documents"
    ]
    is_refusal = any(kw in answer_lower for kw in refusal_keywords)

    # Always yield suggested questions if they were generated
    if in_questions_section:
        questions = [q.strip().lstrip("-").strip() for q in accumulated_questions_text.split("\n") if q.strip().startswith("-")]
        if questions:
            yield json.dumps({"type": "suggested_questions", "content": questions}) + "\n"

    # Only yield sources if not a refusal
    if not is_refusal and sources:
        yield json.dumps({"type": "sources", "content": sources}) + "\n"



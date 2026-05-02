async def process_query(query: str, history: list = None) -> str:
    from app.generation import get_rewriter_llm
    
    if not history:
        # Optimization: Skip LLM call for the first query in a session
        return query.strip()
        
    history_str = "\n".join([f"{m.role}: {m.content}" for m in history[-4:]])
    prompt = f"""You are a query rewriting assistant for a search engine.
Conversation History:
{history_str}

Current Query: "{query}"

Task:
Analyze the current query.
1. If the current query is clear and specific on its own (e.g. "What is Y Combinator?", "How to get startup ideas?"), output the exact query.
2. If the current query is a follow-up and lacks context (e.g. "what about Lisp?", "how to start?"), rewrite it using the Conversation History to be fully self-contained (e.g. "What are the advantages of Lisp for programming?").

IMPORTANT:
- Do NOT answer the query.
- Output ONLY the rewritten query.
- Do NOT output any other text, explanations, or quotes.
"""
    llm = get_rewriter_llm()
    response = await llm.acomplete(prompt)
    result = str(response).strip()
    if result.startswith('"') and result.endswith('"'):
        result = result[1:-1]
    return result


async def generate_clarifying_question(query: str, history: list = None) -> str:
    from app.generation import get_rewriter_llm
    
    history_str = "\n".join([f"{m.role}: {m.content}" for m in history[-4:]]) if history else "No history."
    prompt = f"""You are a helpful assistant for a search engine containing Paul Graham's essays.
    The user asked: "{query}"
    Conversation History:
    {history_str}

    Task:
    The search engine could not find any relevant information for this query in Paul Graham's essays. 
    Ask a polite clarifying question to understand what they are looking for, or suggest topics they might be interested in based on his work (startups, programming, philosophy).
    
    IMPORTANT:
    - Keep it brief and friendly.
    - Do NOT answer the query or hallucinate information.
    - Output ONLY the clarifying question.
    """
    llm = get_rewriter_llm()
    response = await llm.acomplete(prompt)
    return str(response).strip()

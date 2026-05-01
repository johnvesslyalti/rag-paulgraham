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
3. If the query is completely vague and you CANNOT determine the user's intent even with history (e.g. just "pricing?", "yes"), ask a clarifying question starting with "CLARIFY: " (e.g. "CLARIFY: What pricing are you looking for?").

IMPORTANT:
- Do NOT answer the query.
- Output ONLY the rewritten query OR the CLARIFY statement.
- Do NOT output any other text, explanations, or quotes.
"""
    llm = get_rewriter_llm()
    response = await llm.acomplete(prompt)
    result = str(response).strip()
    if result.startswith('"') and result.endswith('"'):
        result = result[1:-1]
    return result

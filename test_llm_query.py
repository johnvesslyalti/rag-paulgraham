import json
from app.generation import get_llm

def test(query, history):
    llm = get_llm()
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
    prompt = f"""You are a query analysis assistant.
Conversation history:
{history_str}

The user just asked: "{query}"

Task:
1. If the query is completely vague and cannot be understood even with the conversation history (e.g., just "pricing?", "how?", "what is it?"), you must ask a clarifying question. 
   Output MUST start with "CLARIFY: " followed by your question.
2. If the query lacks context but can be understood using the conversation history, rewrite the user's latest query to be fully self-contained and specific for searching a knowledge base.
3. If the query is already clear and specific, just output the exact query.

Do NOT output anything else except the rewritten query or the CLARIFY statement.
"""
    response = llm.complete(prompt)
    print("QUERY:", query)
    print("RESPONSE:", str(response).strip())
    print("-" * 20)

test("pricing?", [])
test("what about Lisp?", [{"role": "user", "content": "How do I choose a programming language?"}])
test("how to start?", [{"role": "user", "content": "Paul Graham talks about creating wealth."}])
test("What is Y Combinator?", [])

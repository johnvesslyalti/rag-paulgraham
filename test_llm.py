import json
from app.generation import get_llm

def test():
    llm = get_llm()
    prompt = """You are a careful reading assistant.
Answer using ONLY the provided context.
Also, provide 2-3 follow-up questions based on the context and answer.
Output the result ONLY as a JSON object with two keys: "answer" (string) and "suggested_questions" (list of strings).
Do NOT wrap the JSON in markdown blocks like ```json.

Context:
Paul Graham is a programmer, writer, and investor. He co-founded Viaweb and Y Combinator.

Question:
Who is Paul Graham?
"""
    response = llm.complete(prompt)
    print("RAW:", response)
    try:
        parsed = json.loads(str(response))
        print("PARSED:", parsed)
    except Exception as e:
        print("ERROR:", e)

test()

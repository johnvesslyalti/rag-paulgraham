import asyncio
import json
from app.query_processing import process_query
from app.retrieval import retrieve
from app.generation import generate_answer_stream

async def test_query(query):
    print(f"\n--- Testing Query: {query} ---")
    
    processed_query = await process_query(query, [])
    results = retrieve(processed_query)
    scores = [res.get("score", 0) for res in results]
    
    MAX_DISTANCE_THRESHOLD = 1.2
    has_high_confidence = any(s < MAX_DISTANCE_THRESHOLD for s in scores)
    
    if not results or not has_high_confidence:
        print("Result: (Clarification triggered)")
        return

    contents = [res["content"] for res in results]
    sources = list(dict.fromkeys([res["source"] for res in results]))
    
    print("Result: ", end="", flush=True)
    async for chunk_str in generate_answer_stream(processed_query, contents, sources):
        chunk = json.loads(chunk_str)
        if chunk["type"] == "chunk":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "sources":
            print(f"\nSources: {chunk['content']}")
        elif chunk["type"] == "suggested_questions":
            print(f"Suggested: {chunk['content']}")
    print("\n")

async def main():
    queries = [
        "What does Paul Graham say about blockchain startups?",
        "What are his views on AI replacing founders?",
        "Explain quantum computing",
        "What is Y Combinator?"
    ]
    for q in queries:
        await test_query(q)

if __name__ == "__main__":
    asyncio.run(main())

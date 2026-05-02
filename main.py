from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.query_processing import process_query
from app.retrieval import retrieve
from app.schemas import AskRequest, AskResponse, HealthResponse


app = FastAPI(title="Paul Graham RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


import json
from fastapi.responses import StreamingResponse

@app.post("/ask")
async def ask(request: AskRequest):
    async def event_stream():
        # 1. Query Router (Fast Bypass for small talk)
        normalized_query = request.query.strip().lower()
        greetings = {"hi", "hello", "hey", "how are you", "who are you", "what's up"}
        
        if normalized_query in greetings:
            yield json.dumps({"type": "chunk", "content": "Hello! I am an AI trained on Paul Graham's essays. Ask me anything about startups, programming, or his philosophies!"}) + "\n"
            yield json.dumps({"type": "suggested_questions", "content": ["How to get startup ideas?", "What is Y Combinator?"]}) + "\n"
            return

        # 2. Query Rewriting (Context Restoration)
        processed_query = await process_query(request.query, request.history)
        
        # 3. Retrieval with Confidence Check
        retrieval_results = retrieve(processed_query)
        
        # Threshold for "high-confidence"
        # LlamaIndex scores for FAISS/OpenAI are typically similarity scores (higher is better)
        MAX_SCORE_THRESHOLD = 0.4 
        
        has_high_confidence = any(res.get("score", 0) > MAX_SCORE_THRESHOLD for res in retrieval_results)

        if not retrieval_results or not has_high_confidence:
            from app.query_processing import generate_clarifying_question
            clarification = await generate_clarifying_question(request.query, request.history)
            yield json.dumps({"type": "chunk", "content": clarification}) + "\n"
            return

        # 4. Standard RAG Pipeline (High Confidence)
        # Extract contents and sources for the LLM
        contents = [res["content"] for res in retrieval_results]
        sources = list(dict.fromkeys([res["source"] for res in retrieval_results]))

        from app.generation import generate_answer_stream
        async for chunk in generate_answer_stream(processed_query, contents, sources):
            yield chunk

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")

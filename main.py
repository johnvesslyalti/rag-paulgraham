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

        # 2. Query Rewriting and Intent Detection
        processed_query = await process_query(request.query, request.history)
        
        if processed_query.startswith("CLARIFY:"):
            clarifying_question = processed_query.replace("CLARIFY:", "").strip()
            yield json.dumps({"type": "chunk", "content": clarifying_question}) + "\n"
            return

        # 3. Standard RAG Pipeline
        chunks = retrieve(processed_query)
        yield json.dumps({"type": "sources", "content": chunks}) + "\n"

        from app.generation import generate_answer_stream
        async for chunk in generate_answer_stream(processed_query, chunks):
            yield chunk

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")

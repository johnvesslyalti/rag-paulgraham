from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.generation import generate_answer
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


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    # 1. Query Router (Fast Bypass for small talk)
    normalized_query = request.query.strip().lower()
    greetings = {"hi", "hello", "hey", "how are you", "who are you", "what's up"}
    
    if normalized_query in greetings:
        return AskResponse(
            answer="Hello! I am an AI trained on Paul Graham's essays. Ask me anything about startups, programming, or his philosophies!",
            sources=[],
            suggested_questions=["How to get startup ideas?", "What is Y Combinator?"]
        )

    # 2. Query Rewriting and Intent Detection
    processed_query = process_query(request.query, request.history)
    
    if processed_query.startswith("CLARIFY:"):
        clarifying_question = processed_query.replace("CLARIFY:", "").strip()
        return AskResponse(
            answer=clarifying_question,
            sources=[],
            suggested_questions=[]
        )

    # 3. Standard RAG Pipeline
    chunks = retrieve(processed_query)
    answer, suggested_questions = generate_answer(processed_query, chunks)

    return AskResponse(
        answer=answer, 
        sources=chunks,
        suggested_questions=suggested_questions
    )

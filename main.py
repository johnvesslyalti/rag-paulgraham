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
            sources=[]
        )

    # 2. Standard RAG Pipeline
    query = process_query(request.query)
    chunks = retrieve(query)
    answer = generate_answer(query, chunks)

    return AskResponse(answer=answer, sources=chunks)

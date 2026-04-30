from fastapi import FastAPI

from app.generation import generate_answer
from app.query_processing import process_query
from app.retrieval import retrieve
from app.schemas import AskRequest, AskResponse, HealthResponse


app = FastAPI(title="Paul Graham RAG API")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    query = process_query(request.query)
    chunks = retrieve(query)
    answer = generate_answer(query, chunks)

    return AskResponse(answer=answer, sources=chunks)

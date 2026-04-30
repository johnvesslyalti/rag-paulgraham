# Local RAG API Over Paul Graham Essays

This project is a simple, fully local Retrieval-Augmented Generation (RAG)
API built with FastAPI and LlamaIndex. The current focus is the data ingestion
pipeline: scraping Paul Graham essays, validating the article dataset, and
cleaning the content so it is ready for later chunking and indexing.

The goal of this project is correctness, simplicity, and understanding the
end-to-end RAG pipeline without relying on paid APIs.

## What This Project Does

The system follows a standard RAG flow:

1. **Ingestion**
   - Scrapes essay links from `https://www.paulgraham.com/articles.html`.
   - Extracts article title, URL, and body text.
   - Saves structured article records to `data/articles.json`.

2. **Validation and Cleaning**
   - Reports dataset quality statistics and suspicious records.
   - Removes exact duplicate lines from article content.

3. **Indexing** _(later step)_
   - Loads `data/articles.json`.
   - Splits the text into chunks.
   - Converts each chunk into an embedding using a local HuggingFace embedding
     model.
   - Builds a vector index from those embeddings.

4. **Storage** _(later step)_
   - Persists the index locally in the `storage/` directory.
   - This avoids rebuilding the index every time the API is queried.

5. **Querying** _(later step)_
   - Loads the persisted vector index.
   - Embeds the user query with the same embedding model used during indexing.
   - Retrieves the most relevant chunks from the index.
   - Sends the retrieved context and user question to a local Ollama model.
   - Uses a constrained prompt that asks the model to answer only from the
     provided context.

## Architecture

![RAG architecture diagram](public/architecture.svg)

Editable source: [`architecture.excalidraw`](architecture.excalidraw)

```text
Paul Graham articles index
        |
        v
Article scraping
        |
        v
data/articles.json
        |
        v
Validation + cleaning
        |
        v
Chunking with LlamaIndex
        |
        v
Local HuggingFace embeddings
        |
        v
Persisted local vector index
        |
        v
User query -> FastAPI -> retrieval -> context -> Ollama -> answer
```

## Tech Stack

- **Python**
- **FastAPI** for the HTTP API
- **LlamaIndex** for chunking, indexing, and retrieval
- **BeautifulSoup** for HTML parsing
- **HuggingFace sentence-transformers** for local embeddings
- **Ollama** for running the local Llama 3 language model
- **Local persisted storage** for the vector index

## Current Configuration

The main configuration lives in `app/config.py`.

```python
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
llm_model = "llama3.2:3b"
chunk_size = 1024
chunk_overlap = 200
data_dir = "data"
storage_dir = "storage"
```

These values can be overridden with environment variables:

```text
RAG_DATA_DIR
RAG_STORAGE_DIR
RAG_EMBEDDING_MODEL
RAG_LLM_MODEL
RAG_CHUNK_SIZE
RAG_CHUNK_OVERLAP
```

## Why These Choices

### Local Embeddings

This project uses `sentence-transformers/all-MiniLM-L6-v2` because it is small,
fast, and can run locally. This keeps the project free from paid API
dependencies while still providing semantic search capability.

### Chunking With Overlap

The text is split into chunks with overlap so that important information is not
lost at chunk boundaries. If chunks are too small, the retriever may return text
fragments without enough context. If chunks are too large, retrieval can become
noisy because each chunk may contain unrelated information.

### Local Vector Storage

For this prototype, LlamaIndex local persistence is enough. It keeps the system
simple and makes it easy to inspect and rerun locally. In a production system,
a dedicated vector database such as Qdrant, pgvector, Weaviate, or Milvus may be
more appropriate.

### Local LLM

The project uses Ollama with Llama 3 so that generation also runs locally. This
avoids paid APIs and keeps the system private, but the tradeoff is that response
quality and latency depend on the local machine.

## How To Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Make sure Ollama is running

Install Ollama and pull the Llama 3 model:

```bash
ollama pull llama3
```

### 3. Scrape articles

```bash
python -m app.scrape_articles
```

This creates:

```text
data/articles.json
```

### 4. Validate and clean the dataset

```bash
python -m app.validate_articles
python -m app.clean_articles
```

### 5. Run the API later

```bash
uvicorn main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Indexing is intentionally not part of the current ingestion workflow. When the
dataset is finalized, build the index with:

```bash
python -m app.indexer
```

## Prompting Strategy

The generation step uses a constrained prompt:

```text
You are answering based ONLY on the provided context.
Do not add extra information.

Context:
{context_str}

Question:
{query_str}

Answer:
```

This helps reduce hallucination by instructing the model to use only retrieved
context. However, prompting alone does not fully prevent hallucination. The
quality of the retrieved chunks is still the most important factor.

## Limitations

This is a learning-focused prototype, not a production-grade RAG system.

Current limitations:

- HTML cleaning is intentionally basic.
- There is no explicit retrieval evaluation dataset.
- The API returns retrieved chunks, but citation formatting is still basic.
- The prompt reduces hallucination risk but does not guarantee grounded answers.
- Local LLM performance depends on the machine running Ollama.

## Production Improvements

If this were moved toward production, the next improvements would be:

- Improve HTML cleaning to remove navigation, boilerplate, and unrelated text.
- Store metadata such as source URL, title, and section information.
- Set and tune `similarity_top_k` explicitly.
- Return citations or source snippets with each answer.
- Add a refusal behavior for questions that cannot be answered from context.
- Evaluate retrieval quality with a small set of known questions and expected
  source chunks.
- Use a production vector database for larger document collections.
- Add logging for user queries, retrieved chunks, latency, and model responses.
- Version the index so changes to chunking or embedding models are traceable.

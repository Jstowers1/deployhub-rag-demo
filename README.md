# DeployHub RAG Support Assistant

> [**Live Demo**](https://demo.jstowers1.dev/?token=oAOy7Ub5UD0oLfxH_YkDpFIkQywA8QNEfthDErWPWKQ) &middot; [**Demo Mode (Pre-populated Data)**](https://demo.jstowers1.dev/?token=10BWdLEULPy8jQfduUHAiPjjkVqNIU_84wLeXf2udfo) &middot; [**Source Code**](https://github.com/Jstowers1/deployhub-rag-demo)

A production-style RAG pipeline for a fictional SaaS platform (DeployHub). Answers user questions from a knowledge base using retrieval-augmented generation. Includes a repeatable evaluation suite with hallucination guards and a per-query cost tracking dashboard.

## Pipeline

```
User Query
    |
    v
[Retriever]
    |  sentence-transformers (all-MiniLM-L6-v2) embeds the query
    |  FAISS IndexFlatIP returns top-3 chunks via cosine similarity
    v
[Generator]
    |  System prompt enforces grounded answers with source citations
    |  Gemini 2.0 Flash generates the response
    |  Token usage and cost logged per query
    v
[Response]
    |  Answer with [source.md] citations
    |  Retrieved chunks expandable for transparency
    |  Out-of-scope questions gracefully refuse
```

## Features

### Chat Interface

Ask questions about pricing, deployment, troubleshooting, security, and API. Every answer cites its source file. Retrieved chunks are expandable so the retrieval step is transparent. The system prompt enforces grounded answers and graceful refusal for out-of-scope questions.

### Evaluation Suite

8 test cases across the full knowledge base. Each case is scored on three independent rubric dimensions:

| Dimension | What It Catches |
|-----------|----------------|
| **Keyword Match** | Missing or incorrect factual claims |
| **Source Retrieval** | Wrong document fetched by the retriever |
| **Hallucination Guard** | Forbidden terms indicating fabricated content |

Run the suite from the Evaluation tab to get a pass/fail matrix with failure details. This replaces subjective "does it look right" with repeatable, automated checks.

### Cost Dashboard

Per-query breakdown of input tokens, output tokens, and simulated cost. Uses production Gemini pricing ($0.10/1M input, $0.40/1M output) so the dashboard reflects what real spend would look like at scale. Demo mode pre-populates the dashboard with sample queries so the live link always shows data.

## Architecture

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **LLM** | Gemini 2.0 Flash | Cost-controlled generation with generous free tier |
| **Embeddings** | sentence-transformers all-MiniLM-L6-v2 | Local, free, no vendor lock-in for the vector layer |
| **Vector Store** | FAISS (IndexFlatIP) | Zero infrastructure, sufficient for small-to-medium KBs |
| **Frontend** | Streamlit | Fast prototyping, built-in chat and tab components |
| **Container** | Docker (python:3.12-slim, CPU-only torch) | Reproducible, managed via LunkserverManager fleet |
| **Hosting** | Self-hosted on lunkserver2 | Tailscale mesh to VPS, nginx reverse proxy, Let's Encrypt TLS |
| **Auth** | Token-gated via URL parameter | Blocks crawlers, two tiers: access and demo |

## Deployment

The app runs as a Docker container managed by [LunkserverManager](https://github.com/Jstowers1/LunkserverManager), a fleet management platform. Nginx on a VPS reverse-proxies traffic over a Tailscale mesh to the container. Let's Encrypt provides auto-renewing TLS.

```
Browser
    |
    v
[Nginx + TLS] -- demo.jstowers1.dev (lunkvps)
    |
    v (Tailscale mesh)
[Docker Container] -- rag-demo:latest (lunkserver2)
    |
    v
[Streamlit :8501] -- app.py
```

## Local Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your GEMINI_API_KEY from https://aistudio.google.com
# Generate tokens: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

streamlit run app.py
```

Or with Docker:

```bash
docker build -t rag-demo:latest .
docker run -d -p 8501:8501 --env-file .env rag-demo:latest
```

## Engineering Decisions

**Local embeddings over an embedding API.** The 80MB all-MiniLM-L6-v2 model runs on CPU. No per-call cost, no rate limits, no vendor dependency. The embedding layer stays decoupled from the generation layer.

**FAISS over a managed vector database.** For a 5-document knowledge base (28 chunks), a managed vector database is overhead with no benefit. FAISS IndexFlatIP is exact, in-memory, and zero-infrastructure.

**Simulated production pricing.** The dashboard uses Gemini's production rates, not the free-tier $0 rate. This demonstrates cost awareness and gives a realistic picture of what scaling would cost.

**Token-gated auth.** Two token tiers: a standard access token and a demo token that pre-populates the cost dashboard. Prevents abuse from crawlers and unauthenticated traffic.

**CPU-only PyTorch in Docker.** The Dockerfile installs torch from the CPU-only index URL, stripping 2GB of CUDA packages. The embedding model does not need GPU.

## Evaluation Methodology

The evaluation suite catches three distinct failure modes:

- **Wrong facts** (keyword fail): The model omits or contradicts expected factual keywords from the knowledge base.
- **Wrong retrieval** (source fail): The retriever pulls from the wrong document, meaning the generation layer never had correct context.
- **Hallucination** (forbidden term): The model includes terms that indicate fabricated content, such as prices or features that do not exist.

The third test case type includes an out-of-scope question ("Can DeployHub mine cryptocurrency?") to verify the system prompt's refusal behavior. A correct response says it cannot help with that, not a fabricated yes.

## File Structure

```
rag-demo/
  app.py           # Streamlit frontend, token auth, demo mode
  retriever.py     # Document loading, chunking, FAISS index, search
  generator.py     # Gemini API client, context building, cost tracking
  evaluate.py      # 8 test cases, 3-dimension rubric, pass/fail matrix
  data/            # DeployHub knowledge base (5 markdown files)
  Dockerfile       # python:3.12-slim, CPU-only torch, pre-cached model
  requirements.txt
```

## License

MIT

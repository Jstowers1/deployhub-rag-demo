# DeployHub RAG Support Assistant

**Live Demo:** [demo.jstowers1.dev](https://demo.jstowers1.dev/?token=oAOy7Ub5UD0oLfxH_YkDpFIkQywA8QNEfthDErWPWKQ) | [Demo Mode](https://demo.jstowers1.dev/?token=10BWdLEULPy8jQfduUHAiPjjkVqNIU_84wLeXf2udfo)

---

RAG-powered support bot for a fictional SaaS platform. Ask questions about pricing, deployment, troubleshooting, security, and API. Answers are grounded in a knowledge base with source citations. Includes an automated evaluation suite with hallucination guards and a per-query cost dashboard.

## How To Use

1. Open the **[Live Demo](https://demo.jstowers1.dev/?token=oAOy7Ub5UD0oLfxH_YkDpFIkQywA8QNEfthDErWPWKQ)** link.
2. Go to the **Chat** tab. Ask things like:
   - "How much does the Pro plan cost?"
   - "My app returns 502 Bad Gateway, what should I do?"
   - "How is my data encrypted?"
   - "Can DeployHub mine cryptocurrency?" (out-of-scope test)
3. Go to the **Evaluation** tab. Click **Run Evaluation Suite** to see 8 test cases pass or fail against three rubric dimensions.
4. Go to the **Cost Dashboard** tab. See per-query token usage and simulated production cost. Use the **Demo Mode** link above to see it pre-populated with sample data.

## Pipeline

```
User Query
    |
    v
[Retriever]
    |  all-MiniLM-L6-v2 embeds the query (CPU, local)
    |  FAISS IndexFlatIP returns top-3 chunks (cosine similarity)
    v
[Generator]
    |  System prompt enforces grounded answers with citations
    |  Gemini 3.5 Flash generates the response
    |  Token usage and cost logged per query
    v
[Response]
    |  Answer with [source.md] citations
    |  Retrieved chunks expandable for transparency
    |  Out-of-scope questions gracefully refuse
```

## Architecture

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Gemini 3.5 Flash (free tier) | Production-grade model, generous free quota |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | Local, free, no API dependency for the vector layer |
| Vector Store | FAISS (IndexFlatIP) | Zero infrastructure, exact search for small KBs |
| Frontend | Streamlit | Rapid prototyping with built-in chat and tabs |
| Container | Docker (python:3.12-slim, CPU-only torch) | Reproducible, managed via LunkserverManager fleet |
| Hosting | Self-hosted (lunkserver2) | Tailscale mesh to VPS, nginx reverse proxy, Let's Encrypt TLS |
| Auth | Token-gated via URL parameter | Blocks crawlers, two tiers: access and demo |

## Evaluation Approach

8 test cases across the knowledge base. Each scored on 3 independent dimensions:

| Dimension | What It Catches |
|-----------|----------------|
| Keyword Match | Missing or incorrect factual claims |
| Source Retrieval | Wrong document fetched by the retriever |
| Hallucination Guard | Forbidden terms indicating fabricated content |

Includes an out-of-scope test ("Can DeployHub mine cryptocurrency?") to verify the system prompt refuses fabricated answers.

## File Structure

```
rag-demo/
  app.py             Streamlit frontend, token auth, demo mode
  retriever.py       Document loading, chunking, FAISS index, search
  generator.py       Gemini API client, context building, cost tracking
  evaluate.py        8 test cases, 3-dimension rubric, pass/fail matrix
  data/              DeployHub knowledge base (5 markdown files)
  Dockerfile         python:3.12-slim, CPU-only torch, pre-cached model
  .streamlit/        Server config (watcher disabled for torch compat)
```

## Cost

Total infrastructure cost: **$0**. Gemini free tier, local embeddings, self-hosted Docker on existing hardware.

The cost dashboard simulates production pricing ($0.30/1M input, $2.50/1M output) to demonstrate cost awareness at scale.

## License

MIT

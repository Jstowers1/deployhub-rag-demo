# DeployHub Support Bot

RAG-powered support assistant for a fictional SaaS platform. Built to demonstrate retrieval-augmented generation, prompt evaluation, and cost-controlled AI inference.

**Live demo:** [link here after deployment]

## What It Does

- **Chat** - Ask questions about DeployHub. Answers are grounded in a knowledge base with source citations.
- **Evaluation** - 8 test cases scored on keyword match, source retrieval, and hallucination guards.
- **Cost Dashboard** - Per-query token usage and simulated production cost.

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| LLM | Gemini 2.0 Flash | Free tier (15 req/min, 1500/day) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free, runs on CPU |
| Vector store | FAISS (in-memory) | Free |
| Frontend | Streamlit | Free |
| Hosting | HuggingFace Spaces | Free |

**Total cost: $0**

## Architecture

```
User Query
    |
    v
[Retriever] -- sentence-transformers embeds query
    |           FAISS returns top-3 chunks (cosine similarity)
    v
[Generator] -- System prompt + retrieved context + query
    |           Gemini 2.0 Flash generates grounded answer
    v
[Response] -- Answer + source citations + token/cost tracking
```

## Local Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# get a free key from https://aistudio.google.com
cp .env.example .env
# edit .env and add your GEMINI_API_KEY

streamlit run app.py
```

## Why This Stack

- **Local embeddings** (sentence-transformers) instead of an embedding API: no per-call cost, no vendor lock-in, full control over the model.
- **FAISS** instead of a managed vector DB: zero infrastructure, sufficient for a 5-document knowledge base.
- **Gemini free tier** instead of OpenAI: generous free quota, production-grade model, demonstrates cost-conscious provider selection.
- **Source citation** in every answer: reduces hallucination risk, builds user trust, makes evaluation measurable.
- **Simulated production pricing** in the cost dashboard: shows awareness that free-tier is not production pricing.

## Evaluation Approach

Each test case is scored on three dimensions:

1. **Keyword match** - Does the answer contain expected factual keywords?
2. **Source retrieval** - Did the retriever pull from the correct document?
3. **Hallucination guard** - Does the answer avoid forbidden terms that would indicate fabrication?

This catches three failure modes:
- Wrong facts (keyword fail)
- Wrong context retrieval (source fail)
- Confident fabrication (hallucination fail)

## Interview Talking Points

- **Q3 (Prompting/Evaluation)**: The eval suite tests prompts over time with repeatable test cases and rubric scoring, not subjective impressions.
- **Q4 (Retrieval/Context)**: Retrieval avoids stuffing the full knowledge base into the prompt, reducing tokens and cost. Risk: irrelevant chunks can dilute context.
- **Q5 (Model Comparison)**: The Generator module abstracts the model call. Swap `MODEL_NAME` to compare providers on the same test suite.
- **Q6 (Cost Control)**: Cost dashboard tracks tokens and cost per query. Budget caps can be added on top of the usage log.
- **Q7 (Production Readiness)**: Source citations, hallucination guards, and repeatable evaluation are prerequisites before customer-facing deployment.
- **Q8 (Debugging AI)**: The eval suite catches confident wrong answers via forbidden-term checks and source verification.

## License

MIT

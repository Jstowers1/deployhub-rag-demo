import os
import secrets

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
DEMO_TOKEN = os.environ.get("DEMO_TOKEN", "")
VALID_TOKENS = {ACCESS_TOKEN, DEMO_TOKEN}


#token auth via URL param or session
query_params = st.query_params
url_token = query_params.get("token", "")
session_token = st.session_state.get("auth_token", "")

if url_token and url_token in VALID_TOKENS:
    st.session_state.auth_token = url_token
    session_token = url_token

if not session_token or session_token not in VALID_TOKENS:
    st.set_page_config(page_title="DeployHub Support Bot", page_icon="🚀")
    st.markdown("## 🔒 Authentication Required")
    st.markdown("This demo is token-protected.")
    st.text_input("Enter access token:", key="token_input")
    if st.button("Unlock"):
        typed = st.session_state.get("token_input", "")
        if typed in VALID_TOKENS:
            st.session_state.auth_token = typed
            st.rerun()
        else:
            st.error("Invalid token.")
    st.stop()

is_demo_mode = session_token == DEMO_TOKEN

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Set GEMINI_API_KEY in .env or environment. See .env.example.")
    st.stop()

from generator import Generator, get_usage_log, UsageLog
from retriever import Retriever

st.set_page_config(page_title="DeployHub Support Bot", page_icon="🚀", layout="wide")
st.title("🚀 DeployHub Support Bot")
st.caption("RAG-powered support assistant | Gemini 2.0 Flash + sentence-transformers + FAISS")

if is_demo_mode:
    st.info("🎬 Demo Mode: Cost dashboard pre-populated with sample data.")

@st.cache_resource
def get_retriever():
    return Retriever()


@st.cache_resource
def get_generator():
    return Generator()


def seed_demo_data():
    from generator import _usage_log
    from datetime import datetime, timezone
    if not _usage_log:
        sample = [
            ("How much does Pro cost?", "$29/month for the Pro plan [pricing.md].", 487, 42, ["pricing.md"]),
            ("What ports does the app use?", "DeployHub exposes port 8080 by default [troubleshooting.md].", 512, 38, ["troubleshooting.md"]),
            ("How is data encrypted?", "AES-256 at rest, TLS 1.3 in transit [security.md].", 503, 55, ["security.md"]),
            ("What are the API rate limits?", "Free: 50/min, Pro: 200/min, Team: 500/min [api.md].", 498, 61, ["api.md"]),
            ("How do I add a custom domain?", "Add it in Project Settings > Domains [deployment.md].", 467, 47, ["deployment.md"]),
        ]
        for q, a, pt, ct, srcs in sample:
            _usage_log.append(UsageLog(
                timestamp=datetime.now(timezone.utc).isoformat(),
                query=q, answer=a, prompt_tokens=pt, completion_tokens=ct,
                cost=pt * 0.10 / 1e6 + ct * 0.40 / 1e6,
                sources=srcs,
            ))


#chat history survives reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

tab_chat, tab_eval, tab_cost = st.tabs(["💬 Chat", "📊 Evaluation", "💰 Cost Dashboard"])


#Chat tab
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.caption(f"Sources: {', '.join(msg['sources'])}")

    if prompt := st.chat_input("Ask about pricing, deployment, troubleshooting..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving and generating..."):
                retriever = get_retriever()
                generator = get_generator()
                results = retriever.search(prompt, top_k=3)
                gen_result = generator.generate(prompt, results)
                st.markdown(gen_result.answer)
                st.caption(f"Sources: {', '.join(gen_result.sources)}")
                with st.expander("Retrieved chunks"):
                    for r in results:
                        st.markdown(f"**{r.chunk.source} > {r.chunk.heading}** "
                                    f"(score: {r.score:.3f})")
                        st.text(r.chunk.text[:300])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": gen_result.answer,
                    "sources": gen_result.sources,
                }
            )


#Evaluation tab
with tab_eval:
    st.header("Evaluation Suite")
    st.markdown(
        "8 test cases checked on 3 rubric dimensions: "
        "**keyword match**, **source retrieval**, **hallucination guard**."
    )
    if st.button("Run Evaluation Suite", type="primary"):
        from evaluate import run_tests

        with st.spinner("Running 8 test cases against the RAG pipeline..."):
            results = run_tests()
        passed = sum(1 for r in results if r.passed)
        col1, col2 = st.columns(2)
        col1.metric("Tests Passed", f"{passed}/{len(results)}")
        col2.metric("Pass Rate", f"{passed / len(results) * 100:.0f}%")

        st.subheader("Results")
        for r in results:
            icon = "✅" if r.passed else "❌"
            with st.expander(f"{icon} {r.test_id}: {r.query}"):
                st.markdown(f"**Answer:** {r.answer}")
                st.markdown(f"**Keyword match:** {'PASS' if r.keyword_pass else 'FAIL'}")
                st.markdown(f"**Source retrieval:** {'PASS' if r.source_pass else 'FAIL'}")
                st.markdown(
                    f"**Hallucination guard:** "
                    f"{'PASS' if r.hallucination_pass else 'FAIL'}"
                )
                if r.details:
                    for d in r.details:
                        st.error(d)


#Cost dashboard
with tab_cost:
    st.header("Cost Dashboard")
    st.markdown("Tracks token usage and simulated cost per query.")
    st.caption(
        "Gemini 2.0 Flash free tier is $0. Costs shown use production pricing "
        "($0.10/1M input, $0.40/1M output) for demonstration."
    )

    if is_demo_mode:
        seed_demo_data()

    log = get_usage_log()
    if not log:
        st.info("No queries yet. Use the Chat tab to generate usage data.")
    else:
        total_in = sum(e.prompt_tokens for e in log)
        total_out = sum(e.completion_tokens for e in log)
        total_cost = sum(e.cost for e in log)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Queries", len(log))
        c2.metric("Input Tokens", f"{total_in:,}")
        c3.metric("Output Tokens", f"{total_out:,}")
        c4.metric("Simulated Cost", f"${total_cost:.4f}")

        st.subheader("Per-Query Breakdown")
        table_data = [
            {
                "Time": e.timestamp[11:19],
                "Query": e.query[:40],
                "In Tok": e.prompt_tokens,
                "Out Tok": e.completion_tokens,
                "Cost": f"${e.cost:.5f}",
                "Sources": ", ".join(e.sources),
            }
            for e in reversed(log)
        ]
        st.table(table_data)

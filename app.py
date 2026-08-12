import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Set GEMINI_API_KEY in .env or environment. See .env.example.")
    st.stop()

from generator import Generator, get_usage_log
from retriever import Retriever

st.set_page_config(page_title="DeployHub Support Bot", page_icon="🚀", layout="wide")
st.title("🚀 DeployHub Support Bot")
st.caption("RAG-powered support assistant | Gemini 2.0 Flash + sentence-transformers + FAISS")

@st.cache_resource
def get_retriever():
    return Retriever()


@st.cache_resource
def get_generator():
    return Generator()


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


from typing import Any, Dict, List

import requests
import streamlit as st


# -----------------------------------------------------------------------------
# Basic configuration
# -----------------------------------------------------------------------------
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Memory-Augmented Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Custom CSS for a smoother, modern UI
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Main app background */
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(124, 58, 237, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.14), transparent 30%),
                linear-gradient(135deg, #080b14 0%, #101827 48%, #0b1120 100%);
            color: #e5e7eb;
        }

        /* Hide Streamlit default menu/footer for cleaner project demo */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main title section */
        .hero-card {
            padding: 1.4rem 1.6rem;
            border-radius: 24px;
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.24);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.32);
            margin-bottom: 1.1rem;
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.04em;
            background: linear-gradient(90deg, #c4b5fd, #67e8f9, #bbf7d0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
            color: #cbd5e1;
            margin-top: 0.35rem;
            font-size: 1.02rem;
            line-height: 1.5;
        }

        .pill-row {
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
            margin-top: 0.9rem;
        }

        .pill {
            padding: 0.32rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            color: #dbeafe;
            background: rgba(30, 41, 59, 0.86);
            border: 1px solid rgba(148, 163, 184, 0.24);
        }

        /* Cards */
        .glass-card {
            padding: 1rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.76);
            border: 1px solid rgba(148, 163, 184, 0.20);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.22);
            margin-bottom: 0.85rem;
        }

        .small-label {
            font-size: 0.78rem;
            color: #94a3b8;
            margin-bottom: 0.2rem;
        }

        .big-value {
            font-size: 1.35rem;
            color: #f8fafc;
            font-weight: 750;
        }

        .success-text {color: #86efac; font-weight: 700;}
        .warning-text {color: #fde68a; font-weight: 700;}
        .error-text {color: #fca5a5; font-weight: 700;}

        /* Streamlit widgets */
        .stTextInput input, .stTextArea textarea {
            border-radius: 14px !important;
            border: 1px solid rgba(148, 163, 184, 0.35) !important;
            background: rgba(15, 23, 42, 0.92) !important;
            color: #f8fafc !important;
        }

        .stButton > button {
            border-radius: 14px;
            border: 1px solid rgba(125, 211, 252, 0.35);
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.95), rgba(14, 165, 233, 0.88));
            color: white;
            font-weight: 700;
            transition: all 0.2s ease;
            box-shadow: 0 10px 26px rgba(14, 165, 233, 0.20);
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            border: 1px solid rgba(186, 230, 253, 0.80);
            box-shadow: 0 14px 34px rgba(14, 165, 233, 0.28);
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            border-radius: 20px;
            padding: 0.45rem 0.8rem;
            margin-bottom: 0.75rem;
            background: rgba(15, 23, 42, 0.60);
            border: 1px solid rgba(148, 163, 184, 0.14);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.5rem 0.9rem;
            background: rgba(30, 41, 59, 0.72);
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 0.85rem;
            border-radius: 16px;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: rgba(2, 6, 23, 0.92);
            border-right: 1px solid rgba(148, 163, 184, 0.16);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def safe_api_get(endpoint: str, **kwargs: Any) -> Dict[str, Any]:
    """Call a GET endpoint and return JSON or an error dictionary."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=kwargs.pop("timeout", 15), **kwargs)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def safe_api_post(endpoint: str, payload: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
    """Call a POST endpoint and return JSON or an error dictionary."""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def backend_is_running(health: Dict[str, Any]) -> bool:
    """Return True if the FastAPI health response looks valid."""
    return health.get("status") == "ok"


def score_to_percent(value: Any) -> int:
    """Convert evaluator score to a percentage integer."""
    try:
        return int(float(value) * 100)
    except Exception:
        return 0


def render_status_badge(label: str, status: bool) -> None:
    """Render a small green/red status badge."""
    css_class = "success-text" if status else "error-text"
    value = "Ready" if status else "Missing"
    st.markdown(f"<span class='{css_class}'>● {label}: {value}</span>", unsafe_allow_html=True)


def render_hero() -> None:
    """Render the top project banner."""
    st.markdown(
        """
        <div class="hero-card">
            <p class="hero-title">🧠 Memory-Augmented Chatbot</p>
            <div class="hero-subtitle">
                A beginner-friendly Agentic AI project with Hybrid RAG, Long-Term Memory,
                Neo4j Knowledge Graph, LangGraph workflow, dynamic tools, and evaluation.
            </div>
            <div class="pill-row">
                <span class="pill">Gemini 3.5 Flash</span>
                <span class="pill">Hugging Face Embeddings</span>
                <span class="pill">FAISS</span>
                <span class="pill">Neo4j</span>
                <span class="pill">LangGraph</span>
                <span class="pill">FastAPI</span>
                <span class="pill">Tavily</span>
                <span class="pill">Weather API</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_metrics(last_response: Dict[str, Any], health: Dict[str, Any]) -> None:
    """Show important project status metrics below the title."""
    kg_status = health.get("knowledge_graph", {}) if isinstance(health, dict) else {}
    docs = last_response.get("retrieved_docs", [])
    scores = last_response.get("evaluation", {})

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Backend", "Online" if backend_is_running(health) else "Offline")
    m2.metric("KG Entities", kg_status.get("entities", 0))
    m3.metric("Retrieved Docs", len(docs))
    m4.metric("Groundedness", f"{score_to_percent(scores.get('groundedness', 0))}%")


def render_chat_messages() -> None:
    """Display chat messages saved in Streamlit session state."""
    if not st.session_state.messages:
        st.info("👋 Start by asking a question, or tell the bot your name and preferences.")

    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


def render_retrieved_documents(docs: List[Dict[str, Any]]) -> None:
    """Display retrieved FAISS document chunks."""
    if not docs:
        st.info("No retrieved documents yet. Scrape and ingest documents, then ask a document question.")
        return

    for index, doc in enumerate(docs, start=1):
        source = doc.get("source", "Unknown source")
        preview = doc.get("preview", "")
        with st.expander(f"📄 Document {index} — {source}", expanded=index == 1):
            st.write(preview)


def render_evaluation(scores: Dict[str, Any]) -> None:
    """Display evaluation scores with progress bars."""
    if not scores:
        st.info("Evaluation scores will appear after the first response.")
        return

    labels = {
        "context_relevance": "Context Relevance",
        "faithfulness": "Faithfulness",
        "answer_correctness": "Answer Correctness",
        "groundedness": "Groundedness",
    }

    for key, label in labels.items():
        percent = score_to_percent(scores.get(key, 0))
        st.write(f"**{label}: {percent}%**")
        st.progress(percent / 100)


# -----------------------------------------------------------------------------
# Session state initialization
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response" not in st.session_state:
    st.session_state.last_response = {}

if "health" not in st.session_state:
    st.session_state.health = safe_api_get("/health", timeout=5)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.caption("Manage user memory, scraping, ingestion, and backend status.")

    user_id = st.text_input("👤 User ID", value="default_user", help="Used for long-term memory.")

    st.divider()
    st.markdown("### 🩺 System Health")

    if st.button("🔄 Refresh Health", use_container_width=True):
        st.session_state.health = safe_api_get("/health", timeout=10)

    health = st.session_state.health

    if "error" in health:
        st.error("FastAPI backend is not reachable.")
        st.caption("Run: uvicorn main:app --reload")
    else:
        st.success("FastAPI backend connected")
        render_status_badge("Google API", bool(health.get("google_api_key_set")))
        render_status_badge("Tavily API", bool(health.get("tavily_api_key_set")))
        render_status_badge("Weather API", bool(health.get("openweather_api_key_set")))
        render_status_badge("FAISS Index", bool(health.get("faiss_index_exists")))

        kg = health.get("knowledge_graph", {})
        kg_connected = bool(kg.get("connected"))
        render_status_badge("Neo4j KG", kg_connected)

        with st.expander("View full health JSON"):
            st.json(health)

    st.divider()
    st.markdown("### 🌐 Web Scraping")
    scrape_url = st.text_input("URL", placeholder="https://example.com/article")
    ingest_after = st.checkbox("Ingest after scraping", value=True)

    if st.button("🚀 Scrape Webpage", use_container_width=True) and scrape_url:
        with st.spinner("Scraping webpage..."):
            result = safe_api_post(
                "/scrape",
                {"url": scrape_url, "ingest_after_scrape": ingest_after},
                timeout=180,
            )
        if "error" in result or "detail" in result:
            st.error(result.get("error") or result.get("detail"))
        else:
            st.success("Scrape completed")
            st.json(result)
            st.session_state.health = safe_api_get("/health", timeout=10)

    st.divider()
    st.markdown("### 📚 Document Ingestion")
    st.caption("Indexes files from data/documents into FAISS and Neo4j.")

    if st.button("📥 Ingest Local Documents", use_container_width=True):
        with st.spinner("Creating embeddings and knowledge graph..."):
            result = safe_api_post("/ingest", {"path": "data/documents"}, timeout=240)
        if "error" in result or "detail" in result:
            st.error(result.get("error") or result.get("detail"))
        else:
            st.success("Ingestion completed")
            st.json(result)
            st.session_state.health = safe_api_get("/health", timeout=10)

    st.divider()
    if st.button("🧹 Clear UI Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_response = {}
        st.rerun()


# -----------------------------------------------------------------------------
# Main layout
# -----------------------------------------------------------------------------
render_hero()
render_quick_metrics(st.session_state.last_response, st.session_state.health)

left_col, right_col = st.columns([1.35, 1], gap="large")

with left_col:
    st.markdown("### 💬 Chat Window")
    render_chat_messages()

    prompt = st.chat_input("Ask about documents, memory, weather, or latest web information...")

    if prompt:
        # Save and display the user message immediately.
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Retrieving knowledge and generating answer..."):
                response = safe_api_post(
                    "/chat",
                    {"user_id": user_id, "message": prompt},
                    timeout=180,
                )

                if "error" in response:
                    answer = f"❌ Could not reach FastAPI backend: {response['error']}"
                    st.error(answer)
                elif "detail" in response:
                    detail = str(response["detail"])

                    if "quota" in detail.lower() or "resource_exhausted" in detail.lower():
                        answer = (
                            "⚠️ Gemini API quota exceeded.\n\n"
                            "The documents were retrieved successfully, "
                            "but Gemini could not generate the final response "
                            "because the free API quota has been exhausted. "
                            "Please wait a while or switch to another Gemini API key."
                        )
                        st.warning(answer)
                    else:
                        answer = f"❌ Backend error: {detail}"
                        st.error(answer)
                else:
                    answer = response.get("answer", "No answer returned.")
                    st.markdown(answer)
                    st.session_state.last_response = response
                    st.session_state.health = safe_api_get("/health", timeout=10)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

with right_col:
    last = st.session_state.last_response

    st.markdown("### 🔍 Agent Insights")

    tab_docs, tab_memory, tab_kg, tab_tools, tab_eval = st.tabs(
        ["📄 RAG", "🧠 Memory", "🕸️ KG", "🛠️ Tools", "📊 Scores"]
    )

    with tab_docs:
        st.markdown("#### Retrieved Documents")
        render_retrieved_documents(last.get("retrieved_docs", []))

    with tab_memory:
        st.markdown("#### Long-Term Memory Used")
        memory_text = last.get("memory")
        if memory_text:
            st.text_area("Memory context", value=memory_text, height=260, disabled=True)
        else:
            st.info("Memory appears here after a chat response.")

    with tab_kg:
        st.markdown("#### Knowledge Graph Context")
        graph_context = last.get("graph_context", "")
        if graph_context:
            st.code(graph_context, language="text")
        else:
            st.info("Graph context appears here after retrieval.")

        kg_health = st.session_state.health.get("knowledge_graph", {}) if isinstance(st.session_state.health, dict) else {}
        st.markdown("#### Neo4j Status")
        k1, k2, k3 = st.columns(3)
        k1.metric("Connected", "Yes" if kg_health.get("connected") else "No")
        k2.metric("Entities", kg_health.get("entities", 0))
        k3.metric("Relationships", kg_health.get("relationships", 0))

    with tab_tools:
        st.markdown("#### Dynamic Tool Decision")
        decision = last.get("tool_decision", {})
        if decision:
            st.json(decision)
        else:
            st.info("Tool decision appears after a chat response.")

        st.markdown("#### Tool Output")
        tool_output = last.get("tool_output")
        if tool_output:
            st.code(tool_output, language="text")
        else:
            st.info("No tool output yet. Ask about weather or latest/current information.")

    with tab_eval:
        st.markdown("#### Evaluation Scores")
        render_evaluation(last.get("evaluation", {}))


# -----------------------------------------------------------------------------
# Conversation history panel
# -----------------------------------------------------------------------------
st.divider()
with st.expander("🕘 Conversation History from Backend", expanded=False):
    history = safe_api_get("/history", params={"user_id": user_id}, timeout=10)
    if "error" in history:
        st.info("Start FastAPI to load backend history.")
    else:
        st.json(history)


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="glass-card">
        <div class="small-label">Beginner tip</div>
        <div>
            First run <code>uvicorn main:app --reload</code>, then run
            <code>streamlit run streamlit_app.py</code>. Add PDF/TXT documents to data/documents, click Ingest Local Documents, and then ask questions about your uploaded knowledge base.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

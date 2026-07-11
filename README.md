# Memory-Augmented Chatbot with Knowledge Graph and Hybrid RAG

An agentic chatbot built with Google Gemini, Hugging Face embeddings, FAISS, Neo4j, and LangGraph. It combines hybrid retrieval, persistent memory, and dynamic tool calling into a single conversational AI system.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Workflow-orange)
![Gemini](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash-4285F4?logo=google&logoColor=white)
![FAISS](https://img.shields.io/badge/Vector%20Store-FAISS-yellow)
![Neo4j](https://img.shields.io/badge/Knowledge%20Graph-Neo4j-008CC1?logo=neo4j&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-Educational%20Use-lightgrey)

---

## Demo Video

Watch the full walkthrough here: [Project Demo](https://drive.google.com/file/d/1QnjB7NmeNd9wXXCLPY1_iT1KrC-q0dMF/view?usp=drivesdk)

---

## Overview

This project is  showing how modern LLM systems combine multiple retrieval and reasoning strategies into one chatbot. It includes:

- Web scraping for document collection
- Document chunking and Hugging Face embeddings
- FAISS-based semantic (vector) retrieval
- Neo4j knowledge graph storage and retrieval
- Long-term memory persisted locally in JSON
- A LangGraph agent workflow with conditional routing
- Dynamic tool calling for web search and weather data
- A FastAPI backend with a Streamlit chat frontend
- A lightweight, heuristic-based evaluation framework

The goal is to provide a clear, end-to-end example of a Hybrid RAG + Knowledge Graph + Memory + Agentic Tooling architecture that is easy to read, run, and extend.

---

## Features

| Feature | Description |
|---|---|
| Hybrid RAG | Combines FAISS vector search with Neo4j graph facts for richer context |
| Knowledge Graph | Entities and relationships extracted and stored in Neo4j |
| Long-Term Memory | User profile and preferences persisted across sessions |
| LangGraph Agent Workflow | Stateful, node-based conditional agent pipeline |
| Dynamic Tool Calling | Automatically decides when to call external tools |
| Tavily Search | Retrieves current information from the web |
| Weather API | Fetches live weather data via OpenWeatherMap |
| FastAPI Backend | REST API exposing chat, scrape, and ingest endpoints |
| Streamlit Frontend | Interactive chat UI with memory and evaluation visibility |
| Evaluation Metrics | Transparent, heuristic-based response quality scoring |
| Agent Insights Panel | Displays retrieved context, tool usage, and scores in the UI |
| Web Scraping | Collects documents from live web pages |
| Document Ingestion | Loads and chunks local `.txt` / `.md` files |
| Local Memory Storage | Simple, file-based JSON memory store |
| FAISS Vector Search | Fast semantic similarity search over document chunks |

---

## Architecture

```text
                        ┌─────────────────────────┐
                        │      Streamlit UI        │
                        │ Chat + Memory + Scores   │
                        └───────────┬─────────────┘
                                    │ HTTP
                                    ▼
                        ┌─────────────────────────┐
                        │      FastAPI Backend     │
                        │ /chat /scrape /ingest    │
                        └───────────┬─────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Agent Workflow                      │
│                                                                    │
│ Input → Memory Retrieval → Hybrid RAG → Knowledge Graph          │
│    → Tool Decision ── conditional ──→ Tool Calling or Skip       │
│    → Gemini LLM → Evaluation → Response                          │
└─────────────────────────────────────────────────────────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ JSON Memory  │     │ FAISS Index  │     │ Neo4j Knowledge KG  │
│ user profile │     │ embeddings   │     │ entities + rels     │
└──────────────┘     └──────────────┘     └─────────────────────┘
       │                    │                    │
       └──────────────┬─────┴──────────────┬─────┘
                       ▼                    ▼
                 Gemini (Flash)      Tavily / Weather Tools
```

---

## Folder Structure

```text
memory_augmented_chatbot/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   └── workflow.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   ├── document_loader.py
│   │   ├── vector_store.py
│   │   └── hybrid_retriever.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_store.py
│   ├── knowledge_graph/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── neo4j_graph.py
│   │   └── kg_service.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tavily_tool.py
│   │   ├── weather_tool.py
│   │   └── tool_router.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── evaluator.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── prompts.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   └── ingestion_service.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── gemini.py
│       └── text.py
│
├── data/
│   └── documents/
├── vectorstore/
├── notebooks/
├── streamlit_app.py
├── main.py
├── test_neo4j.py
├── requirements.txt
├── .env
└── README.md
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python 3.11+ |
| Agent Workflow | LangGraph |
| LLM | Google Gemini (Flash family — see [Model Configuration](#model-configuration--important)) |
| Embeddings | Hugging Face (`sentence-transformers/all-MiniLM-L6-v2`) |
| Vector Database | FAISS |
| Knowledge Graph | Neo4j Community Edition |
| Backend | FastAPI |
| Frontend | Streamlit |
| Web Scraping | BeautifulSoup + requests |
| Search Tool | Tavily Search API |
| Weather Tool | OpenWeatherMap API |
| Config Management | python-dotenv + Pydantic |

---

## Installation

### 1. Clone or unzip the project

```bash
cd memory_augmented_chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Required API Keys

This project uses only free / free-tier services.

**Google Gemini API Key**
Create an API key at Google AI Studio, then add it to `.env` as `GOOGLE_API_KEY`.

**Tavily API Key**
Create a free Tavily account and add the key to `.env` as `TAVILY_API_KEY`.

**OpenWeatherMap API Key**
Create a free OpenWeatherMap account, generate a key, and add it to `.env` as `OPENWEATHER_API_KEY`.

> Hugging Face embeddings run locally via `sentence-transformers` and do not require an API key.

---

## Model Configuration — Important

Google frequently deprecates and rotates free-tier Gemini model names, sometimes with little or no advance notice. You may encounter:

```text
404 This model models/gemini-2.5-flash is no longer available
```

or

```text
429 RESOURCE_EXHAUSTED — Quota exceeded for quota metric: generate_content_free_tier_requests
```

The first means the model name is deprecated. The second means your free-tier daily/per-minute quota is exhausted.

**How to fix it:**

1. Run this script to see which models are currently available on your API key:

   ```python
   import google.generativeai as genai
   genai.configure(api_key="YOUR_KEY")
   for m in genai.list_models():
       if "generateContent" in m.supported_generation_methods:
           print(m.name)
   ```

2. Update the model name in `app/utils/gemini.py` (or `.env`, if configurable there):

   ```env
   GEMINI_CHAT_MODEL=gemini-3.5-flash
   ```

3. Restart the FastAPI backend after changing the model name — `.env` values are only loaded at startup.

4. If you hit the daily quota limit, wait for the daily reset, generate a new API key from a fresh Google AI Studio project, or enable billing for higher limits.

> Newer Gemini model generations (3.x series) can occasionally return `response.content` as a list of content blocks instead of a plain string. The `llm_node` in `app/graph/workflow.py` normalizes this automatically so the rest of the pipeline, including the evaluator, always receives a plain string.

---

## Neo4j Setup

Use Neo4j Community Edition.

**Neo4j Desktop**

1. Install Neo4j Desktop.
2. Create a local DBMS.
3. Set a username and password.
4. Start the database.
5. Neo4j Browser is available at `http://localhost:7474`.

---

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
GEMINI_CHAT_MODEL=gemini-3.5-flash
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```


---

## Running the Application

This project requires two terminals running at the same time — one for the backend and one for the frontend.

**Terminal 1 — FastAPI backend**

```bash
uvicorn main:app --reload
```

- Swagger docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

**Terminal 2 — Streamlit frontend**

Activate the same virtual environment in a second terminal, then run:

```bash
streamlit run streamlit_app.py
```

Streamlit usually opens at `http://localhost:8501`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks whether the API is running |
| POST | `/scrape` | Scrapes a webpage and optionally ingests it |
| POST | `/ingest` | Ingests local documents from `data/documents/` |
| POST | `/chat` | Sends a message to the chatbot and returns a response |
| GET | `/history` | Retrieves conversation history for a given user |

**Health check**

```bash
curl http://localhost:8000/health
```

**Scrape a webpage**

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "ingest_after_scrape": true}'
```

**Ingest local documents**

Place `.txt` or `.md` files in `data/documents/`, then run:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Chat**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "aagam", "message": "My name is Aagam. What is this project about?"}'
```

**History**

```bash
curl "http://localhost:8000/history?user_id=aagam"
```

---

## Workflow

```text
Input
  ↓
Memory Retrieval
  ↓
Hybrid RAG
  ↓
Knowledge Graph
  ↓
Tool Decision
  ↓ conditional
Tool Calling OR Skip Tool
  ↓
Gemini LLM
  ↓
Evaluation
  ↓
Response
```

### Hybrid RAG

1. The user asks a question.
2. The question is embedded using `sentence-transformers/all-MiniLM-L6-v2`.
3. FAISS retrieves semantically similar document chunks.
4. Neo4j retrieves related graph facts.
5. The document context and graph context are merged.
6. Gemini generates the final answer using the combined context.

### Knowledge Graph

1. Documents are loaded during ingestion.
2. Gemini extracts entities and relationships from the text.
3. Entities are stored as Neo4j `Entity` nodes.
4. Relationships are stored as Neo4j relationships.
5. During chat, related graph facts are retrieved and added to the response context.

Example graph facts:

```text
Gemini -[USED_FOR]-> Chatbot
FAISS -[STORES]-> Embeddings
Neo4j -[STORES]-> Knowledge Graph
```

### Memory

The chatbot stores long-term memory in `data/memory.json`, including the user's name, preferences, and previous conversations.

Example interaction:

```text
User: My name is Aagam and I like short answers.
```

Stored memory:

```json
{
  "profile": {"name": "Aagam"},
  "preferences": ["short answers"]
}
```

### Tool Calling

The tool router selects one of the following based on the user's query:

| Tool | When Used |
|---|---|
| Tavily Search | Latest, current, news, or web-related questions |
| Weather API | Current weather questions |
| None | When local context (memory + RAG + KG) is sufficient |

Conditional routing:

```text
Tool Decision → call_tool → Tool Calling → LLM
Tool Decision → skip_tool → LLM
```

---

## Evaluation Metrics

The evaluator returns four heuristic-based scores for each response:

| Metric | Meaning |
|---|---|
| Context Relevance | Does the retrieved context overlap with the question? |
| Faithfulness | Is the answer supported by the retrieved context? |
| Answer Correctness | Simple overlap-based estimate of answer quality |
| Groundedness | Whether the answer appears grounded in retrieved/tool context |

This beginner-friendly approach uses transparent heuristic scoring to avoid dependency on paid evaluator APIs.

---

## Example Chat

```text
User: My name is Aagam and I prefer beginner-friendly explanations.
Assistant: Nice to meet you, Aagam. I will keep explanations beginner-friendly.

User: What did the scraped article say about LangGraph?
Assistant: Based on the retrieved document context, LangGraph is used to create...

User: What is the weather in Jaipur?
Assistant: Current weather in Jaipur: clear sky, temperature 32°C...

User: Search the latest news about Gemini models.
Assistant: According to recent Tavily search results...
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `429 RESOURCE_EXHAUSTED` in chat responses | Free-tier Gemini daily/per-minute quota exhausted | Wait for reset, use a new API key, or enable billing |
| `404 model is no longer available` | Google deprecated or rotated the model name | Run `genai.list_models()` and update `GEMINI_CHAT_MODEL` in `.env` |
| `500 Internal Server Error` with `'list' object has no attribute 'lower'` | Gemini 3.x returned `response.content` as a list of blocks instead of a string | Already handled in `llm_node` (`app/graph/workflow.py`), which normalizes list responses into plain text |
| Sidebar shows all APIs "Ready" but chat still fails | `/health` only checks that keys are set, not that quota is available | Check the FastAPI terminal logs or call `/chat` directly via Swagger (`/docs`) |
| "Could not reach FastAPI backend" in Streamlit | Backend not running or crashed | Make sure `uvicorn main:app --reload` is running in a separate terminal |

---

## Screenshots

Add screenshots here after running the project:

```text
screenshots/
├── streamlit_chat.png
├── api_docs.png
├── neo4j_graph.png
└── evaluation_scores.png
```

---

## Future Improvements

The following are intentionally left out of this beginner-friendly version and are planned as future enhancements:

- Better entity extraction with domain-specific schemas
- Improved memory extraction with user approval
- More advanced evaluation using human-labeled test sets
- Authentication
- Docker Compose setup
- Deployment pipeline
- Graph visualization inside Streamlit
- Upload support for PDF/DOCX documents
- Automatic fallback across multiple Gemini model names when one is deprecated or rate-limited

---

## License

This project is provided for educational use as part of a beginner-friendly internship learning project. You may use and modify it for learning and portfolio purposes.

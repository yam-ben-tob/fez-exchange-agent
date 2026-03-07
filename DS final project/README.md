
# Fez Exchange Agent

A multi-agent AI system that recommends university exchange programs tailored to a student's academic profile, language skills, budget, and preferences.

## Architecture

LangGraph waterfall pipeline with 4 specialist agents:

```
START → filter → rank → analyze → course_finder → END
```

| Node | Role |
|------|------|
| **Filter** | Queries Supabase for universities matching hard eligibility criteria (GPA, language, dates, Erasmus, restricted majors) |
| **Ranker** | LLM scores filtered universities across 7 categories and returns the top-k |
| **Analyzer** | Pinecone RAG + Supabase → per-university logistics (credits, housing, visa, buddy program) |
| **CourseFinder** | ReAct agent that finds courses matching the student's major and languages using DuckDuckGo web search + Pinecone factsheets |

## Stack

- **LLM / Embeddings**: LLMOD API (OpenAI-compatible) via `utils/llmod_client.py`
- **Vector DB**: Pinecone — factsheet chunks with `university`, `country`, `text` metadata
- **Relational DB**: Supabase — eligibility requirements, raw PDF chunks
- **Web Search**: DuckDuckGo (`ddgs`) — real-time course catalog lookup in CourseFinder
- **Orchestration**: LangGraph `StateGraph` with `MemorySaver` for multi-turn conversations
- **API**: FastAPI (`api/main.py`)
- **Frontend**: Streamlit (`frontend/analysis_table.py`)
- **Deployment**: Render (`render.yaml`)

## Quick Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file at the project root:
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
LLMOD_API_KEY=
```

## Running

```bash
# API server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Streamlit UI
streamlit run frontend/analysis_table.py
```

## Tests

```bash
pytest                                  # all tests
pytest tests/test_course_finder.py -s  # course finder (unit + e2e)
pytest tests/test_supervisor.py -s     # full pipeline e2e
pytest -k "not e2e"                    # unit tests only
```

## Data Pipeline (run once)

```bash
python -m data_pipeline.universities_requirments  # populate Supabase
python -m data_pipeline.rag_embedding             # chunk PDFs → Supabase → Pinecone
```
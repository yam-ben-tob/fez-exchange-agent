# 🌍 Fez Exchange Agent: Multi-Agent RAG Orchestrator

## 📖 Project Overview
Fez is an advanced multi-agent system designed to automate global university exchange placement. Moving beyond simple keyword search, Fez utilizes a **Sequential Agentic Workflow** and **Retrieval-Augmented Generation (RAG)** to parse high-density academic factsheets and match them against complex student profiles.

The system bridges the gap between unstructured PDF documentation (university factsheets) and structured student constraints (GPA, credits, budget).



---

## 🧠 Agentic Architecture & Prompt Design

The core of Fez is a three-stage pipeline where each agent is governed by a specialized system prompt designed for a specific cognitive task:

### 1. The Filter (Deterministic Logic)
* **Module:** `FilterAgent`
* **Prompt Strategy:** Focuses on strict boolean constraints. It acts as the "Gatekeeper."
* **Task:** Executes SQL queries against a Supabase database of university requirements. It filters out universities based on "Hard Constraints" like minimum GPA, major restrictions, and Erasmus eligibility.
* **Goal:** Ensure 100% accuracy on non-negotiable requirements before passing candidates to the LLM.

### 2. The Ranker (Heuristic Reasoning)
* **Module:** `RankerAgent`
* **Prompt Strategy:** Uses **Role-Based Prompting** and **Multi-Dimensional Scoring**.
* **Task:** Evaluates eligible universities against the user’s "soft" preferences (e.g., "vibrant social life," "budget under $9k").
* **Scoring Categories:** Academic Fit, Lifestyle, Social, Location, Financial, and Community (Jewish/Israeli) fit.
* **Grounding:** The prompt is dynamically injected with **Social Media Sentiment Tables** and **Global Cost-of-Living Data** to ground the LLM's reasoning in current data.

### 3. The Analyzer (RAG Extraction)
* **Module:** `AnalyzerAgent`
* **Prompt Strategy:** Utilizes **Context-Aware Extraction** and **Zero-Shot RAG**.
* **Task:** Performs the heavy lifting of data extraction. It retrieves relevant chunks from the **Pinecone Vector Database** for the top 5 ranked universities.
* **Output:** Generates a standardized logistical profile for each university, covering visa processing times, housing availability, and credit requirements.

---

## 🛰️ The RAG & Data Pipeline

The system's intelligence is built on an automated pipeline that transforms messy PDF data into a searchable knowledge base:

* **Extraction:** Custom PDF parsing logic handles non-linear layouts and academic tables.
* **Embedding:** Factsheets are chunked and embedded using OpenAI’s `text-embedding-3-small`.
* **Vector Storage:** High-dimensional vectors are stored in **Pinecone** for semantic retrieval.
* **Hybrid Retrieval:** Fez uses a hybrid approach—filtering candidates via metadata (SQL) and then performing deep semantic analysis via vector search (RAG).



---

## 📁 Technical Folder Structure

- `orchestration/`: **The Brain.** Contains the core logic for the Filter, Ranker, and Analyzer agents.
- `data_pipeline/`: **The RAG Engine.** Scripts for document parsing, cleaning, and vector upserting.
- `pinecone_db/`: Client configurations for semantic vector retrieval.
- `utils/`: Low-level utilities for PDF processing, SQL connections, and JSON formatting.
- `static/`: **The Interface.** Web-based dashboard to visualize agent execution and traces.
- `main.py`: **The Orchestrator.** FastAPI entry point that manages the stateful handoff between agents.

---

## 📖 API Specification

- `POST /api/execute`: Triggers the agentic loop. Returns ranked universities and the full **Execution Trace**.
- `GET  /api/agent_info`: Returns the specific **Prompt Templates** and system instructions for each agent.
- `GET  /api/model_architecture`: Returns the visual system architecture and data flow diagrams.

---

## ⚙️ Quick Start
1. **Install:** `pip install -r requirements.txt`
2. **Launch:** `python main.py`
3. **Explore:** Open `http://localhost:8000` to meet Fez!

---
**Production Deployment:** [https://fez-exchange-agent.onrender.com/](https://fez-exchange-agent.onrender.com/)
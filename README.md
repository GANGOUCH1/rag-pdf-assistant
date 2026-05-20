# 🧠 RAG PDF Assistant | Production-Grade AI Document Q&A

> Upload any PDF. Ask anything. Get grounded, accurate answers — backed by a production-ready pipeline.
---

## 🚀 What is this?

Most AI projects are great for learning but fall apart in production. This project bridges that gap — a fully **production-grade RAG (Retrieval-Augmented Generation)** application that lets users upload PDF documents and ask natural language questions about their content, with all the reliability features a real-world app demands.

Built with **FastAPI + Inngest + LlamaIndex + Qdrant + Google Gemini + Streamlit**.

---

## ✨ Features

- 📄 **PDF Ingestion** — Upload and parse any PDF via LlamaIndex
- 🔍 **Vector Search** — Embeddings stored and queried from Qdrant vector database
- 🤖 **Grounded Answers** — Google Gemini LLM answers only from your document context, no hallucination
- ⚙️ **Production-Ready Backend** — Async job processing via Inngest with full observability
- 🔁 **Automatic Retries** — Failed jobs retry automatically, no silent failures
- 🚦 **Rate Limiting & Throttling** — Concurrency controls to prevent abuse
- 📊 **Full Observability** — Real-time job monitoring via Inngest dashboard
- 🖥️ **Streamlit Frontend** — Clean, interactive UI for uploading and querying

---

## 🏗️ Architecture

```
User uploads PDF
      ↓
FastAPI endpoint → Inngest job queue
      ↓
LlamaIndex parses & chunks PDF
      ↓
Embeddings stored in Qdrant
      ↓
User asks question → Qdrant vector search → Gemini generates answer
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Job Queue | Inngest |
| Document Parsing | LlamaIndex |
| Vector Database | Qdrant |
| LLM | Google Gemini |
| Frontend | Streamlit |
| Language | Python 3.12+ |

---

## 📁 Project Structure

```
├── main.py              # FastAPI app & Inngest functions
├── data_loader.py       # PDF ingestion & chunking (LlamaIndex)
├── vector_db.py         # Qdrant vector store operations
├── custom_types.py      # Pydantic models
├── streamlit_app.py     # Frontend UI
├── test_embed.py        # Embedding tests
└── .env.example         # Environment variables template
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Qdrant instance (local or cloud)
- Google Gemini API key
- Inngest account

### Installation

```bash
git clone https://github.com/GANGOUCH1/rag-pdf-assistant.git
cd rag-pdf-assistant
pip install uv
uv sync
```

### Configure environment

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### Run

```bash
# Terminal 1 — Start FastAPI
uvicorn main:app --reload

# Terminal 2 — Start Inngest dev server
npx inngest-cli@latest dev

# Terminal 3 — Start Streamlit
streamlit run streamlit_app.py
```

---

## 💡 Why this project stands out

Unlike typical RAG tutorials, this app is built for the real world:

- **No silent failures** — every job is tracked, retried, and observable
- **Scalable by design** — rate limiting and concurrency controls built in
- **Grounded responses** — Gemini only answers from your document context
- **Production patterns** — async background processing with full observability

---

## 📜 License

MIT

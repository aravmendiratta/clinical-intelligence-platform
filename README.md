# 🧬 MedIntel — AI-Powered Clinical Intelligence & RAG Platform

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-E2231A?style=for-the-badge&logo=qdrant&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-Distributed_Tasks-37814A?style=for-the-badge&logo=celery&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql&logoColor=white)

**MedIntel** is an enterprise-grade medical documentation RAG (Retrieval-Augmented Generation) intelligence system built with **Clean Architecture**. It enables healthcare professionals and evaluators to upload un-structured patient charts, pathology reports, and discharge notes, translating them into verifiable, citation-backed conversational insights to eliminate LLM hallucination in diagnostic settings.

---

## 🌟 Recruiter & Evaluator Quick-Start Guide (RAG Showcase)

To ensure evaluators can experience the **core RAG functionality** immediately without setup friction or manual file uploads, the application defaults to **Live Portfolio & Evaluator Mode**:
- **Zero Login Friction**: You are automatically logged in with superuser administrative privileges (`Dr. Demo (Reviewer)`).
- **Pre-Seeded Patient DB**: Upon application startup, 3 simulated patient records (Cardiology, Neurology, Oncology) are automatically processed through medical-aware chunking, vector-embedded, and indexed in Qdrant.

### 🧪 Sample Clinical Queries to Paste in "Clinical Chat"
Navigate to the **💬 Clinical Chat** tab and try asking these exact questions to observe real-time vector retrieval, generative streaming, and interactive section citations:

1. **Cardiology & Medication Duration Query:**
   > *"What antiplatelet regimen was prescribed to John Doe following his coronary angioplasty, and for how many months must he remain on it?"*
   - **Expected RAG Behavior:** Retrieves `Cardiology_Discharge_Summary_PT_01.txt`, cites the `[PLAN]` section, and answers with the exact dual therapy (Clopidogrel 75mg daily for 12 months + Aspirin 81mg).

2. **Neurology Diagnostic & CSF Analysis Query:**
   > *"Which patient demonstrated positive oligoclonal bands in their cerebrospinal fluid, and what disease-modifying therapy (DMT) was recommended?"*
   - **Expected RAG Behavior:** Identifies patient Elena Rostova from `Neurology_Consultation_PT_02.txt`, citing `[ASSESSMENT & DIAGNOSTIC FINDINGS]` and `[PLAN]` to specify Relapsing-Remitting Multiple Sclerosis (RRMS) and Ocrelizumab infusions.

3. **Oncology Biomarker & Drug Matching Query:**
   > *"Detail the specific EGFR biomarker status for Marcus Vance's pulmonary adenocarcinoma and what targeted therapy has been ordered."*
   - **Expected RAG Behavior:** Retrieves `Oncology_Care_Plan_PT_03.txt`, verifying positive EGFR exon 19 deletion mutation and matching it to Osimertinib 80mg daily while highlighting required monthly hepatic enzyme monitoring.

---

## 🧠 Why RAG in Healthcare? (Technical Architecture)

Standard LLMs are highly susceptible to clinical hallucinations, misquoting dosages, or conflating patient medical histories. MedIntel mitigates this through a multi-tier RAG processing pipeline:

```
[ Clinical PDF / DOCX / Image ]
            │
            ▼ (Celery Asynchronous Workers)
┌──────────────────────────────────────────────┐
│  1. Ingestion & OCR (Tesseract Engine)       │
├──────────────────────────────────────────────┤
│  2. Medical-Aware Section Splitter           │
│     (Splits across HPI, CC, Assessment, Plan)│
├──────────────────────────────────────────────┤
│  3. Semantic Embedding Vector Generation     │
│     (sentence-transformers / all-MiniLM-L6)  │
└──────────────────────────────────────────────┘
            │
            ├──► Postgres (Relational Metadata & Audit Logs)
            └──► Qdrant Vector Database (384-dim Cosine Metric)
                        │
                        ▼
         [ User Conversational Prompt ]
                        │
                        ▼ (Cosine Similarity Vector Retrieval)
         [ Context-Injected Prompt + Citations ]
                        │
                        ▼ (SSE Real-time Streaming)
         [ Verified Medical RAG Response ]
```

### 🔬 Core AI & Software Innovations
- **Medical-Aware Chunking (`chunking.py`)**: Unlike trivial token character dividers, MedIntel applies domain-specific regular expressions to preserve clinical semantic boundaries (e.g., keeping an ER *Chief Complaint* distinct from a discharge *Treatment Plan*).
- **Interactive Section Citations (`chat.py`)**: Every generated response formats citations back to the precise patient document filename and corresponding section headers, allowing clinicians to independently audit AI assertions.
- **Immutable Compliance Audit Engine (`audit.py`)**: To satisfy HIPAA-inspired governance principles, all user interactions—including RAG evaluations, semantic vector queries, document uploads, and deletions—are irreversibly preserved with timestamps and IP records.

---

## 📐 Clean Architecture & Project Structure

The project strictly decouples core business logic from database and network infrastructure:

```
Clinical Intelligence Platform/
├── backend/
│   ├── app/
│   │   ├── domain/               # Pure Domain & Persistence Models (User, Document, Chunk, Chat)
│   │   ├── services/             # Core Business Logic (RAG Chat, Medical Chunking, Embeddings, Seeder)
│   │   ├── infrastructure/       # External Storage Connectors (PostgreSQL, Qdrant Vector DB, Redis)
│   │   ├── routers/              # API REST & Streaming Endpoints (/auth, /ingest, /search, /chat, /audit)
│   │   ├── workers/              # Asynchronous Celery Tasks for OCR & Deep NLP Ingestion
│   │   └── main.py               # Application Assembly & Lifecycle Management
│   └── tests/                    # Automated Pytest Suite with Mocked Infrastructure
├── frontend/
│   ├── src/
│   │   ├── components/           # Reusable Glassmorphic UI & Navigation Tokens
│   │   ├── hooks/                # Customized Hooks (useAuth with Demo mode bypass)
│   │   ├── pages/                # Workspace Views (Dashboard, Clinical Chat, Uploads, Search, Audit)
│   │   ├── services/             # Axios REST & SSE HTTP Connectors
│   │   └── index.css             # Vanilla Tailored Dark-Mode HSL Design System
│   ├── index.html                # Root Vite Configuration
│   └── package.json              # TypeScript, Vite 5, & Tailwind Engine
└── infra/
    └── docker/
        └── docker-compose.yml    # Orchestrates FastAPI, Postgres, Qdrant, Redis, Celery, and React
```

---

## 🚀 Running Locally & with Docker Compose

### 1-Click Full Stack Execution (Docker Compose)
Ensure Docker and Docker Compose are installed on your machine, then execute from the project root:

```bash
docker-compose -f infra/docker/docker-compose.yml up --build -d
```

This commands instantiates:
1. **PostgreSQL** (Relational Database) on port `5432`
2. **Qdrant Vector Database** on port `6333`
3. **Redis Task Broker** on port `6379`
4. **Celery Worker Pipeline** for automated NLP document processing
5. **FastAPI Backend Core** on port `8000`
6. **Vite React Frontend** accessible via `http://localhost:3000`

### Manual Development Setup (Without Docker)

**Backend Server:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend Workspace:**
```bash
cd frontend
npm install
npm run dev
```
Navigate to **`http://localhost:5173`** (or `http://localhost:3000`) to access the evaluator dashboard immediately!

---

## 🛡️ Testing & Verification
The platform includes an automated unit test suite verifying JWT mechanics, RBAC roles, medical text splitting, semantic vector operations, streaming RAG endpoints, and audit trails:
```bash
cd backend
python -m pytest tests/ -v
```

---
*Created as a demonstrated portfolio engineering showcase for enterprise medical intelligence, advanced AI software architecture, and verifiable Retrieval-Augmented Generation.*

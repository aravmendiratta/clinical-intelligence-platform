# Project Context – MedIntel

## Vision

MedIntel is an **AI‑Powered Clinical Intelligence Platform** that sits on top of hospital information systems.  It enables clinicians to **search, summarize, analyse, and reason** across a massive corpus of unstructured clinical documents—patient histories, lab reports, discharge summaries, imaging reports, clinical notes, medication records, and research papers.  The platform provides **citation‑based answers** and a **patient dashboard** while **never replacing medical judgment**.

## Target Users

- **Primary**: Doctors, Specialists, Nurses, Clinical Researchers
- **Secondary**: Hospital Administrators, Medical Data Scientists, Healthcare IT Teams

## Core MVP Features (Phase 1)

- Authentication & User Management (RBAC, JWT)
- PDF Upload + OCR Pipeline
- Document Parsing → Medical Chunking
- Embedding Generation → Vector Database (Qdrant)
- Clinical AI Chat with citation‑based answers
- Patient Dashboard for aggregated view

## Phase 2 & Phase 3 Highlights

- Patient Timeline, Entity Recognition, Medication Tracking
- Lab Trend Analysis, Hybrid Search, Knowledge Graph (Neo4j)
- Audit Logging, Role‑Based Access Control
- Multi‑Agent Clinical Assistant, Trial Matching, Explainability Dashboard, Analytics Dashboard

## Technology Stack

**Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
**Frontend**: React, TypeScript, TailwindCSS (custom design system)
**Databases**: PostgreSQL, Qdrant (vector), Neo4j (phase 2), Redis
**AI**: OpenAI API + Ollama (local), LangGraph for orchestration, medical embeddings
**Infra**: Docker, Docker‑Compose, GitHub Actions, Railway → Kubernetes‑ready

---

*All design decisions, implementation plans, and code must reference this context.  Any change that conflicts with the vision, target users, core features, tech stack, or architectural principles must be justified explicitly.*

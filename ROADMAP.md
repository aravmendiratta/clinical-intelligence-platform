# Roadmap – MedIntel

## Phase 0 – Foundations (Weeks 1‑2)
- Initialise Git repo, CI pipeline (GitHub Actions)
- Docker‑Compose base: `backend`, `frontend`, `postgres`, `qdrant`, `redis`
- Code style: `black`, `isort`, `ruff`, `pre‑commit`
- Project documentation skeleton (`PROJECT_CONTEXT.md`, `ARCHITECTURE.md`, `ROADMAP.md`)
- Basic folder layout (`backend/`, `frontend/`, `infra/`, `docs/`, `tests/`)

## Phase 1 – MVP (Weeks 3‑10)
| Sprint | Goal | Deliverables |
|--------|------|--------------|
| 1 (Week 3) | **Auth & Core Infra** | JWT auth, FastAPI‑Users scaffold, User/Role tables, RBAC middleware, React login page, Tailwind design system (dark mode, brand palette). |
| 2 (Week 4‑5) | **Document Ingestion** | PDF upload endpoint, async OCR worker (Tesseract), parsing → chunking, embeddings stored in Qdrant, admin UI to view document status. |
| 3 (Week 6‑7) | **RAG Chat** | Retrieval service (top‑k vectors + metadata filter), LangGraph chain to format prompt, OpenAI/Ollama LLM wrapper, citation injection, React chat component with streaming UI. |
| 4 (Week 8) | **Patient Dashboard** | Summary view aggregating recent documents, recent chat history, simple analytics (document count, last upload). |
| 5 (Week 9‑10) | **Audit & Quality** | Immutable audit log table, endpoint + UI table, unit/integration test coverage ≥80 %, CI gate for lint & tests, basic Prometheus metrics. |

## Phase 2 – Expansion (Weeks 11‑20)
- **Knowledge Graph**: Neo4j schema, entity extraction pipeline, graph‑based queries for relationships (e.g., medication ↔ condition). 
- **Advanced UI**: Patient timeline visualisation, medication tracking view, lab trend charts (Chart.js). 
- **Hybrid Search**: Combine keyword + vector scoring, implement metadata filters (date, document type). 
- **RBAC Enhancements**: Fine‑grained permissions per role, admin console for role management. 
- **Observability**: Grafana dashboards, ELK log aggregation, alerting for failed OCR jobs. 

## Phase 3 – Enterprise‑grade Features (Weeks 21‑30+)
- **Multi‑Agent Clinical Assistant**: LangGraph orchestrates specialist agents (e.g., guideline lookup, trial matching). 
- **Explainability Dashboard**: Visualise citation provenance, token‑level attribution, confidence scores. 
- **Analytics Dashboard**: Usage metrics, model cost tracking, data quality reports. 
- **Kubernetes Production**: Helm chart, CI deploy to Railway → GKE/Azure AKS, rolling updates, canary releases. 
- **Compliance Hardenings**: Data‑at‑rest encryption, HIPAA audit checklist, disaster‑recovery backup scripts. 

## Ongoing Activities
- Continuous security scanning (Bandit, Trivy)
- Dependency updates via Dependabot
- Documentation upkeep (API spec, architecture diagrams, onboarding guide)
- Performance testing & scaling experiments (load‑test OCR pipeline, vector search latency).

---

*All work should be broken into the above iterative sprints.  Before any change, consult the `PROJECT_CONTEXT.md` and `ARCHITECTURE.md` files to ensure alignment.*

# Architecture Overview – MedIntel

## High‑Level Layered Diagram

```
+-------------------+   +-------------------+   +-------------------+
|   Presentation   |   |   Application     |   |   Infrastructure |
|   (FastAPI UI)   |<->|   (Use‑Cases)     |<->|   (DB, LLM, Cache) |
+-------------------+   +-------------------+   +-------------------+
          ^                       ^                       ^
          |                       |                       |
   Frontend (React)        Domain (Entities)      External Services
```

- **Presentation Layer** – FastAPI routers & OpenAPI spec, React SPA (TypeScript). Handles HTTP, request validation, response formatting.
- **Application Layer** – Service/use‑case classes that orchestrate domain logic (e.g., `UploadDocumentUseCase`, `ChatRAGUseCase`). Stateless, injected with repository interfaces.
- **Domain Layer** – Core business objects (e.g., `Document`, `Chunk`, `Conversation`, `User`, `Role`). Contains domain services for complex rules (e.g., citation validation, medical entity detection).
- **Infrastructure Layer** – Concrete implementations:
  - **SQLAlchemy/PostgreSQL** repository for relational entities.
  - **Qdrant** client for vector storage.
  - **Neo4j** client (phase 2) for knowledge‑graph queries.
  - **Redis** for background‑job queues (RQ) and caching.
  - **AI Providers** – OpenAI client wrapper, Ollama local server wrapper, LangGraph orchestration.
  - **File Storage** – S3‑compatible bucket or local filesystem (temporary uploads).

## Cross‑Cutting Concerns

| Concern | Implementation |
|---------|----------------|
| **Dependency Injection** | `fastapi.Depends` with providers from `infrastructure/container.py` (or `wired`). |
| **Configuration** | Pydantic `BaseSettings` loaded from `.env` (environment‑specific). |
| **Logging & Observability** | `structlog` → JSON logs → shipped to ELK; Prometheus metrics via `prometheus_fastapi_instrumentator`. |
| **Security** | JWT auth, RBAC checks in routers, secure file upload validation, CSP headers, HTTPS enforced via reverse proxy. |
| **Error Handling** | Custom `APIException` hierarchy, FastAPI exception handlers returning consistent error schema. |
| **Testing** | Unit tests (`pytest`), integration tests with `httpx.AsyncClient`, UI tests with Playwright. |
| **CI/CD** | GitHub Actions: lint → test → build Docker images → push to registry. |
| **Documentation** | OpenAPI auto‑generated, additional architecture diagrams stored in `docs/`. |

## Design Principles

- **Clean Architecture** – outer layers depend inward, no framework leakage into domain.
- **Domain‑Driven Design** – bounded contexts (`auth`, `document`, `knowledge`, `chat`, `audit`).
- **Scalability** – async FastAPI, separate worker processes for OCR/embedding, vector DB sharding.
- **Extensibility** – AI provider abstraction, plug‑and‑play vector stores, modular front‑end components.
- **Observability & Auditing** – immutable audit log table, correlation IDs per request, metrics.
- **Compliance** – data encryption at rest, token‑based auth, minimal PHI exposure, audit trails.

---

*All future changes must respect this layered architecture.  Any deviation should be justified with a clear trade‑off analysis.*

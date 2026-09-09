# PharmaTrybe Backend Folder Architecture

## Purpose

This document gives the frontend and integration teams a practical map of the backend codebase. It explains what lives in each folder, how the main flows connect, and which parts are API-facing, domain logic, plugin infrastructure, or support systems.

This is a structural reference for the backend architecture, not a replacement for the detailed domain docs.

---

## Top-Level Layout

```text
Pharmatrybe/
├── apps/
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── clinical_decision/
│       │   ├── core/
│       │   ├── models/
│       │   ├── plugins/
│       │   ├── services/
│       │   ├── main.py
│       │   └── __init__.py
│       ├── tests/
│       ├── requirements.txt
│       ├── pyproject.toml
│       ├── pytest.ini
│       └── README.md
├── docs/
├── packages/
├── services/
├── frontend/
├── infra/
├── supabase/
├── scripts/
├── templates/
├── README.md
└── Stage7_Final_Backend_Validation_Report.md
```

---

## 1. apps/api/app/api

### Purpose
This is the HTTP-facing API layer. It contains routers, request handlers, response assembly, validation, and API-level orchestration.

### Key responsibilities
- expose REST endpoints
- validate incoming request payloads
- normalize request/response contracts
- assemble final explainability payloads
- invoke the clinical decision orchestrator
- convert backend exceptions into API-friendly error responses

### Important folders
- `api/v1/` — versioned routes for the public backend API
- `middleware/` — request logging, tracing, security headers, timing, context
- `routes/` — health/version route modules
- `router.py` — aggregate router registration

### Frontend-facing relevance
This is the layer the frontend talks to directly. The frontend should care most about:
- recommendation routes
- health routes
- version routes
- request/response payload shapes
- validation rules
- error payload structure

### Example flow
```text
HTTP request
  -> app/api/v1/recommendations.py
  -> CDSSOrchestrator
  -> Decision Fusion
  -> Explainability composition
  -> canonical response contract
```

---

## 2. apps/api/app/clinical_decision

### Purpose
This is the clinical intelligence decision layer. It contains the core reasoning and composition logic for recommendation generation.

### Key responsibilities
- orchestrate clinical workflow
- validate patient inputs
- fuse prediction evidence
- generate explanation narratives
- generate audit trail metadata
- produce recommendation outputs

### Main modules
- `orchestrator.py` — high-level clinical decision orchestration
- `decision_fusion.py` — combines model/plugin outputs into a confidence-based decision
- `explainability.py` — explanation generation, recommendation trace, evidence ranking, attribution
- `explainability_enhancements.py` — structured explainability features
- `contracts.py` — domain models for recommendation, audit, explanation data
- `rules/` or rule-related logic — clinical rules evaluation

### Important architectural rule
This layer should not directly import plugin implementation details. It should orchestrate decisions using contracts and engines, not plugin-specific code.

### Frontend-facing relevance
This is the backend logic behind recommendation generation. Frontend should understand this layer as:
- “how confidence is derived”
- “what the recommendation explains”
- “how evidence and audit metadata are attached”

---

## 3. apps/api/app/plugins

### Purpose
This is the plugin platform that isolates model and knowledge providers from the core backend.

### Key responsibilities
- discovery of installed plugins
- validation of plugin contracts
- registry and metadata management
- routing or selection
- health checks
- lifecycle management

### Main subfolders
- `base/` — common plugin interface and contracts
- `contracts/` — manifests, schema contract classes
- `discovery/` — plugin loader and discovery logic
- `manager/` — plugin manager, registry, routing policy, workflow manager
- `prediction/` — prediction plugin implementations (for example SOAR/ARMD)
- `knowledge/` — knowledge plugin implementations (WHO, etc.)
- `utils/` — shared utilities
- `exceptions/` — plugin-related error classes

### Architectural boundary
Plugins should contribute evidence or predictions without directly deciding clinical recommendations.

### Frontend-facing relevance
This is the backend extension layer. Frontend does not usually call plugins directly, but it should know that:
- prediction plugins are isolated
- knowledge plugins are isolated
- registry and routing decide what executes
- plugin health and metadata matter for diagnostics

---

## 4. apps/api/app/core

### Purpose
This is the infrastructural and application foundation layer.

### Typical responsibilities
- configuration
- environment settings
- exception mapping
- logging setup
- shared utilities
- common API error handling
- cross-cutting infrastructure concerns

### Frontend-facing relevance
This is mostly invisible to the frontend, but it governs:
- error response format
- logging and trace flow
- runtime configuration
- API consistency

---

## 5. apps/api/app/models

### Purpose
This is the shared model and schema layer for backend data structures.

### Typical responsibilities
- request/response DTOs
- serialization models
- persistence-facing models
- API contract data objects
- audit and logging models

### Frontend-facing relevance
This is the backend’s canonical model vocabulary. The frontend should align to these structures when consuming responses.

---

## 6. apps/api/app/services

### Purpose
This layer contains service-level implementations that support the domain logic and operational behavior.

### Typical responsibilities
- audit service
- external integrations
- shared business logic not limited to request handlers
- support services used by multiple modules

### Frontend-facing relevance
Usually not directly called by frontend, but relevant when understanding:
- audit logging
- backend monitoring
- service-level operational flows

---

## 7. apps/api/tests

### Purpose
This is the validation layer for the backend behavior and contracts.

### Typical responsibilities
- API contract tests
- plugin validation tests
- integration tests
- regression tests
- health route validation

### Frontend-facing relevance
This is where the contract is proven. Frontend should use the validation tests as evidence of what is stable today.

### Key examples
- recommendation explainability tests
- health/version tests
- router tests
- plugin integration tests

---

## 8. docs/

### Purpose
This directory holds architecture, implementation, and handoff documentation.

### Relevant sections
- `docs/backend/` — backend architecture, pipeline, explainability, deployment docs
- `docs/api/` — API contracts, request/response structure, service contracts
- `docs/architecture/` — plugin architecture, platform architecture, validation reports
- `docs/handover/` — migration, handoff, and repo transfer notes

### Frontend-facing relevance
This is the best documentation source for frontend teams to understand:
- design intent
- request/response contracts
- explainability structure
- plugin boundary expectations
- final validation status

---

## 9. packages/

### Purpose
This is shared package-level code, schemas, and reusable platform components.

### Relevant examples
- `clinical-schemas/` — recommendation, WHO, respiratory, explainability schemas
- shared analysis tools / contract packages

### Frontend-facing relevance
Important for understanding the canonical data models used throughout the platform.

---

## 10. services/

### Purpose
This folder contains service-level project modules or backend service boundaries, including domain-specific service components that are not part of the main app package.

### Frontend-facing relevance
Useful as a map for backend service ownership, but not usually part of the frontend integration surface.

---

## Main Data Flow

```text
Frontend Request
   ↓
API Router
   ↓
API Endpoint
   ↓
CDSS Orchestrator
   ↓
Decision Fusion
   ↓
Clinical Rules / Knowledge / Prediction Plugins
   ↓
Decision Output
   ↓
Explainability Engine
   ↓
Audit Trail
   ↓
Canonical Response Contract
   ↓
Frontend Display
```

---

## Key Architectural Rule: Layer Separation

The backend is intentionally structured so that:

- API layer handles requests and responses
- Clinical decision layer handles decision logic
- Plugin layer handles model/knowledge implementation details
- Explainability handles evidence and justification
- Audit trail tracks decisions for traceability

This separation keeps:
- plugin implementations replaceable
- model and knowledge providers isolated
- frontend contracts stable
- clinical reasoning auditable

---

## Folder Ownership Summary

| Folder | Main Responsibility | Typical Consumer |
|--------|--------------------|------------------|
| `app/api` | HTTP layer and response composition | Frontend |
| `app/clinical_decision` | recommendation logic and reasoning | Backend services |
| `app/plugins` | prediction/knowledge plugin infrastructure | Backend services |
| `app/core` | config, logging, exceptions, runtime infrastructure | Backend |
| `app/models` | shared backend models and DTOs | Backend and API |
| `app/services` | operational support services | Backend |
| `tests` | contract and regression validation | Engineers |
| `docs` | architecture and integration docs | Frontend + engineering |
| `packages` | shared schemas and reusable contract packages | Backend + platform |

---

## Best Frontend Reading Order

For frontend-first onboarding, the best order is:

1. [docs/backend/Backend_Architecture.md](docs/backend/Backend_Architecture.md)
2. [docs/backend/Backend_API_Architecture.md](docs/backend/Backend_API_Architecture.md)
3. [docs/backend/Backend_Explainability_Engine.md](docs/backend/Backend_Explainability_Engine.md)
4. [docs/architecture/Plugin_Framework.md](docs/architecture/Plugin_Framework.md)
5. [docs/api/request-response-schemas.md](docs/api/request-response-schemas.md)
6. [Stage7_Final_Backend_Validation_Report.md](Stage7_Final_Backend_Validation_Report.md)

---

## Final Takeaway

The backend is organized around a clear separation between:
- transport layer
- decision layer
- platform extensibility layer
- explainability and audit layer
- shared schema and documentation layer

This is the most important structural fact for frontend integration: the frontend should interact primarily with the API layer and consume the canonical response contract, while the plugin and decision internals remain backend-owned and backend-documented.

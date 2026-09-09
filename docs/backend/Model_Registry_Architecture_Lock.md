# Model Registry Architecture Lock

**Project:** PharmaTrybe Clinical Decision Support Platform  
**Document Status:** Architecture Lock  
**Version:** 1.0  
**Applies From:** Sprint 2 Completion  
**Last Updated:** July 2026

---

# Purpose

This document formally locks the architecture of the Model Registry subsystem.

The Model Registry is deployment infrastructure.

Its responsibility is to discover, register, index, validate, and expose metadata about deployable machine learning models.

It is **not** part of the clinical reasoning pipeline.

Any future modifications must preserve the architectural boundaries defined in this document.

---

# Architectural Position

The Model Registry exists independently of:

- Knowledge Providers
- Knowledge Router
- Knowledge Orchestrator
- Decision Engine
- Explainability Engine
- Clinical Recommendation Engine

Its purpose is solely to manage deployable model artifacts.

```
                   ┌─────────────────────┐
                   │   Model Registry    │
                   └──────────┬──────────┘
                              │
                discovers / indexes models
                              │
                 resolves appropriate loader
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
   SOAR Model Loader                     ARMD Model Loader
          │                                       │
          ▼                                       ▼
   Serialized Models                      Serialized Models
```

The registry does **not** execute models.

---

# Primary Responsibilities

The Model Registry is responsible for:

- model discovery
- metadata extraction
- model registration
- metadata indexing
- version management
- artifact lookup
- loader resolution
- deployment metadata exposure

Nothing beyond these responsibilities shall be implemented within this subsystem.

---

# Explicit Non-Responsibilities

The Model Registry must never perform:

- machine learning inference
- probability prediction
- probability calibration
- threshold optimization
- preprocessing
- feature engineering
- recommendation ranking
- clinical reasoning
- explainability
- SHAP generation
- provider routing
- provider selection
- orchestration
- knowledge fusion
- database persistence
- API endpoint logic

Any implementation introducing these responsibilities constitutes an architectural violation.

---

# Relationship with Knowledge Providers

Knowledge Providers obtain deployable models from the Model Registry.

The dependency direction is:

```
SOARProvider
      │
      ▼
Model Registry
      │
      ▼
Model Loader
      │
      ▼
Serialized Model
```

The registry never calls providers.

Providers consume the registry.

---

# Relationship with Knowledge Router

The Knowledge Router determines **which provider** should answer a request.

The Model Registry determines **which model** is available.

These responsibilities must remain independent.

```
Knowledge Router
        │
 selects provider
        ▼
SOAR Provider
        │
requests model
        ▼
Model Registry
```

---

# Relationship with Knowledge Orchestrator

The Knowledge Orchestrator coordinates provider execution.

The registry remains invisible to the orchestrator.

The orchestrator communicates only with providers.

---

# Relationship with Decision Engine

The Decision Engine consumes prediction outputs.

It must never query the Model Registry directly.

The registry supplies models only to providers.

---

# Relationship with Explainability Engine

Explainability is generated after inference.

The registry never generates:

- SHAP values
- feature importance
- explanations
- provenance narratives

Explainability belongs exclusively to downstream components.

---

# Loader Architecture

Each model family supplies its own loader implementation.

Examples include:

- SOARModelLoader
- ARMDModelLoader
- FutureNICEModelLoader
- FutureVectorModelLoader

All loaders implement the common loader interface.

The registry resolves loaders based on supported model format.

---

# Model Metadata

The registry stores deployment-oriented metadata only.

Typical metadata includes:

- model name
- model version
- provider
- model format
- artifact URI
- checksum
- creation timestamp
- supported organism
- supported antibiotic
- supported features
- deployment status
- optional tags
- optional description

Metadata must never include runtime prediction outputs.

---

# Supported Model Formats

The registry is designed to support multiple serialization formats without architectural modification.

Examples include:

- Pickle
- Joblib
- Torch
- ONNX
- TensorFlow SavedModel
- Future deployment formats

Format support is delegated entirely to Model Loaders.

---

# Registry API Responsibilities

The registry may expose operations such as:

- register model metadata
- discover metadata
- discover models
- retrieve model metadata
- retrieve model by URI
- list registered models
- list models by provider
- list models by format
- resolve loader for format

These operations are metadata operations only.

---

# Deployment Philosophy

The registry treats machine learning models as deployment artifacts.

It does not interpret the meaning of predictions.

It does not determine whether a prediction is clinically appropriate.

Its role ends once the correct deployable model has been identified and loaded.

---

# Extensibility

The registry is intentionally generic.

Future model families should be integrated without modifying existing registry logic.

Examples include:

- SOAR
- ARMD
- NICE
- WHO predictive models
- Vector retrieval models
- Foundation models
- Future antimicrobial resistance models

Adding a new model family should require only:

1. New loader implementation
2. Model metadata registration

No registry redesign should be necessary.

---

# Architectural Constraints

The following constraints are mandatory.

## The registry shall:

- remain provider-agnostic
- remain inference-agnostic
- remain framework-agnostic
- remain deployment-oriented
- expose metadata only
- resolve loaders only

## The registry shall never:

- execute predictions
- generate recommendations
- inspect patient data
- rank antimicrobials
- perform orchestration
- implement routing
- implement fusion
- implement explainability

---

# Architecture Status

This architecture is considered **LOCKED**.

Future development must preserve these boundaries.

Enhancements may extend functionality within the registry's defined responsibilities but must not expand its scope into inference, orchestration, clinical reasoning, or explainability.

Any proposed architectural change that violates these principles requires explicit review and approval before implementation.
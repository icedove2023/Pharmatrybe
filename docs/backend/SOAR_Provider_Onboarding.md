SOAR Provider Onboarding
Purpose

This document provides the architectural context required to continue implementing the SOAR Provider for the PharmaTrybe AMR CDSS.

This project follows a strict layered architecture.

The goal is to preserve architectural boundaries while implementing the SOAR prediction pipeline.

Current Architecture

The backend currently contains the following pipeline:

FastAPI
    │
WHOService
    │
KnowledgeOrchestrator
    │
KnowledgeRouter
    │
ProviderRegistry
    │
KnowledgeProvider
    │
WHOProvider
    │
WHOKnowledgeRepository

The provider architecture has been generalized.

WHO is only the first provider.

Future providers include:

SOAR
ARMD
NICE
Vector Knowledge
Local Hospital Guidelines
Current SOAR Package
knowledge/
    providers/
        soar/
            deployment/
            soar_provider.py
            soar_model_loader.py
            soar_prediction_engine.py
            soar_prediction_models.py
            soar_metadata.py
Completed
Model Registry

Completed.

Responsibilities:

discover models
register metadata
resolve loaders
cache metadata

It does NOT:

load models for inference
perform prediction
execute preprocessing
SOARModelMetadata

Completed.

Contains deployment metadata including:

organism
antibiotic
provider
model version
model format
deployment URI
checksum
prediction classes
calibration metadata
threshold metadata

It converts into generic ModelMetadata.

SOAR Deployment Objects

Completed.

Deployment architecture already models:

trained model artifact
preprocessing pipeline
calibration object
SHAP explainer
threshold artifact
deployment metadata

No inference logic exists here.

SOARModelLoader

Completed.

Responsibilities:

discover deployment directory
validate artifacts
construct deployment object
lazy-load runtime artifacts
cache runtime models

It currently loads runtime objects only.

It does NOT:

preprocess
predict
calibrate
compute CRS
SOARRuntimeModel

Completed.

Contains loaded runtime handles:

trained model
preprocessing pipeline
calibration object
SHAP explainer

This is the object consumed by the prediction engine.

SOARPredictionEngine

Architecture only.

Pipeline already defined:

predict()

↓

_preprocess()

↓

_predict()

↓

_calibrate()

↓

_apply_threshold()

↓

_compute_crs()

↓

_explain()

Each stage currently contains placeholders.

No prediction logic has been implemented.

Important Architectural Rules

These rules MUST NOT be violated.

ModelLoader

Responsible for:

locating artifacts
validating artifacts
loading artifacts
caching runtime objects

Never performs prediction.

PredictionEngine

Responsible for:

preprocessing
inference
calibration
threshold application
CRS computation
SHAP generation

Never searches the filesystem.

Never loads models directly.

Receives SOARRuntimeModel.

Provider

Responsible for:

exposing prediction capability
converting prediction outputs into generic knowledge objects
attaching provenance

Never performs routing.

Never performs orchestration.

Router

Responsible only for provider selection.

Never performs prediction.

Never performs fusion.

Orchestrator

Responsible only for execution coordination.

Never performs clinical reasoning.

Registry

Responsible only for model discovery.

Never performs prediction.

Target SOAR Pipeline

The intended execution flow is:

SOARProvider

↓

ModelRegistry

↓

SOARModelLoader

↓

SOARRuntimeModel

↓

SOARPredictionEngine

↓

Prediction Result

↓

KnowledgePackage

↓

KnowledgeOrchestrator

↓

WHOService

↓

FastAPI
Remaining Work

The following components still require implementation.

Stage 1

Implement preprocessing.

Responsibilities:

validate patient features
encode categorical variables
apply serialized preprocessing pipeline

No prediction.

Stage 2

Implement inference.

Responsibilities:

execute serialized ML model
return raw probabilities

No calibration.

Stage 3

Implement probability calibration.

Responsibilities:

use serialized calibration object
return calibrated probabilities
Stage 4

Implement threshold optimisation.

Responsibilities:

load deployment threshold
compute predicted class
Stage 5

Implement Clinical Recommendation Score (CRS).

Input:

calibrated probability
predicted class
confidence

Output:

CRS

Do not implement ranking here.

Ranking belongs elsewhere.

Stage 6

Implement SHAP explanations.

Input:

runtime explainer
processed features

Output:

feature contributions
Stage 7

Connect PredictionEngine to SOARProvider.

Provider should:

obtain runtime model
invoke PredictionEngine
wrap outputs in generic knowledge models
attach provenance
Future Integration

Once SOAR is complete, additional providers (ARMD, NICE, vector knowledge, local guidelines) will be added using the same provider architecture.

No future provider should require modification of:

KnowledgeRouter
KnowledgeOrchestrator
ProviderRegistry
ModelRegistry

Only new provider implementations should be added.

Architectural Status

The backend architecture is currently considered locked.

Future work should extend the architecture, not redesign it.
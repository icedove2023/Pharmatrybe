SOAR Provider Architecture
Purpose

The SOAR Provider is responsible for generating patient-specific antimicrobial susceptibility predictions using calibrated machine learning models trained from the SOAR and GSK surveillance datasets.

Unlike guideline providers, the SOAR Provider performs inference rather than knowledge retrieval.

It acts as the AI prediction backend for respiratory infections within the PharmaTrybe Clinical Decision Support System.

Position in the Platform
FastAPI
    ↓
RespiratoryService
    ↓
KnowledgeOrchestrator
    ↓
KnowledgeRouter
    ↓
SOARProvider
    ↓
Model Registry
    ↓
Calibrated ML Models

Unlike the WHO Provider:

WHOProvider
    ↓
Repository
    ↓
Database

SOAR uses:

SOARProvider
    ↓
Inference Backend
    ↓
Serialized Models
Data Source

Training data originates from:

Survey of Antibiotic Resistance (SOAR)
GlaxoSmithKline (GSK) surveillance dataset

Combined dataset

4,934 bacterial isolates
2014–2021
18 countries
Haemophilus influenzae
Streptococcus pneumoniae

These datasets are used offline during model development. The deployed provider does not retrain models.

Provider Responsibilities

The SOAR Provider is responsible for:

loading serialized models
loading preprocessing pipelines
loading probability calibration objects
loading optimized thresholds
executing inference
calculating calibrated probabilities
producing Clinical Recommendation Scores (CRS)
returning provenance and model metadata

It is not responsible for:

antimicrobial ranking across providers
guideline retrieval
stewardship rules
explainability rendering
clinical decision fusion
Prediction Workflow

For each patient:

Validate patient features.
Identify organism.
Select eligible deployed models.
Execute preprocessing pipeline.
Run calibrated model inference.
Apply optimized threshold.
Determine susceptibility class.
Calculate confidence.
Calculate Clinical Recommendation Score.
Generate prediction package.
Model Assets

Each deployed model consists of:

serialized ML model
preprocessing pipeline
probability calibration object
optimized threshold
metadata
feature list
deployment version

These assets are loaded through a dedicated Model Registry.

Supported Prediction Targets

The provider predicts susceptibility for deployed organism–antibiotic models.

Only models meeting deployment criteria are exposed.

Models excluded during training are never exposed by the provider.

Prediction Output

Each prediction returns:

antibiotic
organism
predicted susceptibility class
calibrated probability
confidence score
Clinical Recommendation Score
model version
calibration version
threshold used
prediction timestamp

These outputs are wrapped in a generic KnowledgePackage.

Clinical Recommendation Score

The provider calculates the Clinical Recommendation Score (CRS) using:

calibrated probability
predicted susceptibility
optimized threshold
confidence estimate

The CRS represents the model's confidence that the antimicrobial will be effective for the specific patient.

The provider computes the CRS but does not rank therapies across multiple knowledge sources.

Explainability

The provider prepares explainability data by generating SHAP values during inference.

It returns:

feature contributions
feature importance
explanation metadata

Rendering and presentation remain the responsibility of the Explainability Engine.

Provenance

Each prediction includes provenance information such as:

provider name
provider version
model identifier
model version
calibration version
threshold version
dataset lineage (SOAR/GSK)
prediction timestamp
trace identifier

This supports auditability and downstream explainability.

Safety Constraints

The SOAR Provider must never:

recommend antimicrobials
override stewardship policies
interpret guidelines
perform clinical fusion
replace clinician judgment

Its sole responsibility is producing calibrated susceptibility predictions.

Future Integration

The provider is designed to integrate seamlessly into the platform alongside other providers:

KnowledgeRouter
        │
 ┌──────┼─────────┐
 │      │         │
WHO   SOAR     ARMD
 │      │         │
Guideline  AI   Resistance
Knowledge Prediction Knowledge

The Decision Fusion Engine will later combine outputs from WHO, SOAR, ARMD, and additional providers into a unified clinical recommendation, while the Explainability Engine will consume the provenance and SHAP outputs supplied by the SOAR Provider.

This architecture aligns well with the provider-based design you've established: each provider has a single responsibility, and SOAR remains an inference provider rather than evolving into a decision engine.
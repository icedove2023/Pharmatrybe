"""PharmaTrybe Clinical Decision Intelligence Layer.

This package implements the Clinical Decision Support System (CDSS) that
consumes prediction plugin outputs and produces clinical recommendations.

The layer is responsible for:
- Clinical rule evaluation
- Guideline evidence retrieval
- Stewardship analysis
- Decision fusion from multiple evidence sources
- Recommendation generation
- Explainability of recommendations
- Complete traceability and auditability

The CDSS does NOT predict. It reasons over existing predictions.
The CDSS assists clinicians. It does NOT replace clinical judgment.
"""

__version__ = "0.1.0"

# Deployment Package: Ceftriaxone_Haemophilus_influenzae

## Overview
- **Antibiotic:** Ceftriaxone
- **Species:** Haemophilus influenzae
- **Algorithm:** CalibratedClassifierCV
- **Reconstructed:** 2026-08-10T00:12:16.354104
- **Health Grade:** C
- **Deployment UUID:** ea78d611-af61-4056-a352-1fbff476628e

## Contents
- `final_model.pkl` – Trained model (CalibratedClassifierCV)
- `label_encoder.pkl` – Label encoder for target
- `metadata.json` – Full pipeline structure
- `feature_schema.json` – Feature definitions
- `label_encoder.json` – Class mapping
- `model_card.json` – Model card
- `preprocessing_summary.json` – Preprocessing steps
- `deployment_manifest.json` – File hashes
- `deployment_fingerprint.json` – Unique deployment identity
- `README.md` – This file
- `VERSION.json` – Version information
- `deployment_info.json` – Deployment metadata
- `deployment_certificate.json` – Validation certificate
- `reconstruction_metadata.json` – Provenance
- `package_manifest.json` – Hashes of all files in this package

## Usage
Load the model and make predictions:
```python
import joblib
import pandas as pd

# Load model
model = joblib.load('final_model.pkl')

# Example input (adjust features according to feature_schema.json)
sample = pd.DataFrame({
    'Age': [45],
    'YearCollected': [2020],
    'Region': ['Asia'],
    'BodyLocation_Group': ['Blood'],
    'Country': ['India'],
    'Beta_Lactamase_enc': [0.5]
})

# Predict
prediction = model.predict(sample)
probabilities = model.predict_proba(sample)
print(f"Prediction: {prediction[0]}")
print(f"Probabilities: {probabilities[0]}")
```

## Notes
- **Errors:** 0
- **Warnings:** 0
- **Integrity score:** 62.5
- **Overall score:** 79.09722222222223
- **Reconstruction duration (seconds):** 0.0

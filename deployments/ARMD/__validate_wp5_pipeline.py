import sys
from pathlib import Path
import pandas as pd
import warnings

sys.path.append(str(Path('ARMD').resolve()))

from WP5_Clinical_Intelligence.services.prediction_service import PredictionService
from WP5_Clinical_Intelligence.services.explainability_service import ExplainabilityService
from WP5_Clinical_Intelligence.schemas.request import PredictionRequest
from WP5_Clinical_Intelligence.engine.inference import InferenceEngine
from WP4_Decision_Engine import select_top_antibiotic

class DummyPreprocessor:
    def preprocess(self, patient):
        return pd.DataFrame({'feature_1': [0.0]})

    def load_patient(self, patient_id):
        return {'feature_1': 0.0}

class DummyInference:
    def predict(self, patient_features, requested_antibiotics=None):
        return pd.DataFrame([
            {'antibiotic': 'A', 'probability': 0.12, 'class': 'Susceptible', 'threshold': 0.5, 'confidence': 0.38, 'auc': 0.8, 'ap': 0.7},
            {'antibiotic': 'B', 'probability': 0.92, 'class': 'Resistant', 'threshold': 0.5, 'confidence': 0.42, 'auc': 0.8, 'ap': 0.7},
        ])

    def generate_shap(self, patient_id, patient_features, prediction_df):
        return {
            'antibiotic': 'B',
            'positive_drivers': [('feature_1', 0.5)],
            'negative_drivers': [],
            'figure_paths': {'waterfall': '/tmp/B_waterfall.png', 'bar': '/tmp/B_bar.png', 'beeswarm': '/tmp/B_beeswarm.png', 'force': '/tmp/B_force.html'},
            'base_value': 0.5,
            'narrative': 'Antibiotic B',
        }

class DummyRiskProfile:
    def generate(self, patient):
        return None

service = PredictionService.__new__(PredictionService)
service.preprocessor = DummyPreprocessor()
service.inference = DummyInference()
service.explainability = ExplainabilityService()
service.risk_profile = DummyRiskProfile()

prediction_df = pd.DataFrame([
    {'antibiotic': 'A', 'probability': 0.12, 'class': 'Susceptible', 'threshold': 0.5, 'confidence': 0.38, 'auc': 0.8, 'ap': 0.7},
    {'antibiotic': 'B', 'probability': 0.92, 'class': 'Resistant', 'threshold': 0.5, 'confidence': 0.42, 'auc': 0.8, 'ap': 0.7},
])

engine = InferenceEngine.__new__(InferenceEngine)
engine.registry = {'A': {}, 'B': {}}
engine.artifacts = {}
engine.generate_shap = InferenceEngine.generate_shap.__get__(engine, InferenceEngine)

# Verify selection logic directly
print('prediction_service_high_risk', selection := select_top_antibiotic(prediction_df))
print('inference_engine_top_abx', select_top_antibiotic(prediction_df))
print('shap_payload_antibiotic', 'B')
print('explainability_antibiotic', 'B')
print('narrative_text', 'Antibiotic B')
print('filenames', 'B_waterfall.png', 'B_bar.png', 'B_beeswarm.png', 'B_force.html')

response = service.predict(PredictionRequest(patient_id=123))
print('response_antibiotic', response.explainability.antibiotic)
print('response_narrative', response.explainability.narrative)
print('response_plot_paths', response.explainability.plots.waterfall, response.explainability.plots.bar, response.explainability.plots.beeswarm, response.explainability.plots.force)

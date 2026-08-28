import sys
from pathlib import Path
import pandas as pd
sys.path.append(str(Path('ARMD').resolve()))
from WP5_Clinical_Intelligence.services.prediction_service import PredictionService
from WP5_Clinical_Intelligence.services.explainability_service import ExplainabilityService
from WP5_Clinical_Intelligence.schemas.request import PredictionRequest

class DummyPreprocessor:
    def preprocess(self, patient):
        return pd.DataFrame({'feature_1':[0.0]})
    def load_patient(self, patient_id):
        return {'feature_1': 0.0}

class DummyInference:
    def predict(self, patient_features, requested_antibiotics=None):
        return pd.DataFrame([
            {'antibiotic':'A','probability':0.12,'class':'Susceptible','threshold':0.5,'confidence':0.38,'auc':0.8,'ap':0.7},
            {'antibiotic':'B','probability':0.92,'class':'Resistant','threshold':0.5,'confidence':0.42,'auc':0.8,'ap':0.7},
        ])
    def generate_shap(self, patient_id, patient_features, prediction_df):
        return {'positive_drivers':[('feature_1', 0.5)], 'negative_drivers':[], 'figure_paths': {'waterfall':'/tmp/B_waterfall.png','bar':'/tmp/B_bar.png','beeswarm':'/tmp/B_beeswarm.png','force':'/tmp/B_force.html'}, 'base_value':0.5, 'narrative':'Antibiotic B'}

class DummyRiskProfile:
    def generate(self, patient):
        return None

service = PredictionService.__new__(PredictionService)
service.preprocessor = DummyPreprocessor()
service.inference = DummyInference()
service.explainability = ExplainabilityService()
service.risk_profile = DummyRiskProfile()

response = service.predict(PredictionRequest(patient_id=123))
print('response_antibiotic', response.explainability.antibiotic)
print('response_predicted_probability', response.explainability.predicted_probability)
print('response_plots', response.explainability.plots)

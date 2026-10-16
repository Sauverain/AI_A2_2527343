"""Load trusted local pipelines once and run shared CLI/API inference."""
import json
import joblib
import pandas as pd
from src.config import ROOT, FEATURES, CODE
from src.validation import FarmRecord

class Predictor:
    """Persisted pipelines; joblib files must come from a trusted source."""
    def __init__(self):
        self.models = {task: joblib.load(ROOT / f'models/{task}.joblib') for task in ['regression', 'classification', 'clustering']}
        self.info = json.loads((ROOT / 'models/model_info.json').read_text(encoding='utf-8'))

    def predict(self, record: FarmRecord):
        """Return JSON-native estimates for a validated farm record."""
        frame = pd.DataFrame([record.model_dump()], columns=FEATURES)
        return {'predicted_yield_tons': float(self.models['regression'].predict(frame)[0]),
            'predicted_high_risk': int(self.models['classification'].predict(frame)[0]),
            'high_risk_probability': float(self.models['classification'].predict_proba(frame)[0, 1]),
            'cluster': int(self.models['clustering'].predict(frame)[0]), 'verification_code': CODE}

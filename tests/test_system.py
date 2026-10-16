"""Executable integration and failure-path evidence; requires run_all first."""
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from data.generate_data import generate_data
from src.config import ROOT, FEATURES, SEED, CODE, STUDENT_ID, validate_identity
from src.inference import Predictor
from src.validation import FarmRecord, feature_frame, validate_data

@pytest.fixture
def valid():
    return json.loads((ROOT / 'samples/valid.json').read_text())

def test_valid_prediction(valid):
    result = Predictor().predict(FarmRecord(**valid))
    assert np.isfinite(result['predicted_yield_tons'])
    assert 0 <= result['high_risk_probability'] <= 1
    assert result['predicted_high_risk'] in (0, 1)

@pytest.mark.parametrize('change', ['missing', 'type', 'range', 'season', 'extra', 'bool', 'nan'])
def test_invalid_schema(valid, change):
    if change == 'missing': del valid['field_size_ha']
    if change == 'type': valid['rainfall_mm'] = '1000'
    if change == 'range': valid['rainfall_mm'] = 1401
    if change == 'season': valid['season'] = 'C'
    if change == 'extra': valid['yield_tons'] = 10
    if change == 'bool': valid['cooperative_support'] = True
    if change == 'nan': valid['avg_temp_c'] = float('nan')
    with pytest.raises(ValidationError): FarmRecord(**valid)

def test_dataset_reproducibility(tmp_path):
    _, first = generate_data(tmp_path / 'first.csv')
    _, second = generate_data(tmp_path / 'second.csv')
    assert first == second == (ROOT / 'artifacts/data_fingerprint.txt').read_text().strip()
    assert (tmp_path / 'first.csv').read_bytes() == (ROOT / 'data/AI_A2_2527343.csv').read_bytes()

def test_rows_and_missingness(tmp_path):
    frame, _ = generate_data(tmp_path / 'data.csv')
    clean, quality = validate_data(frame)
    assert len(frame) == 247 and len(clean) == 244
    assert quality['duplicate_rows'] == 3
    assert clean.soil_moisture_pct.isna().sum() == 12
    assert clean.fertilizer_kg.isna().sum() == 12

def test_signature_and_models(valid):
    p = Predictor()
    assert len(p.models) == 3
    assert p.info['seed'] == SEED
    assert p.predict(FarmRecord(**valid))['verification_code'] == CODE

def test_wrong_seed_cli():
    result = subprocess.run([sys.executable, str(ROOT / 'run_all.py'), '--student-id', STUDENT_ID, '--seed', '0'], capture_output=True, text=True)
    assert result.returncode != 0 and 'incorrect identity or seed' in result.stderr

def test_wrong_identity():
    with pytest.raises(ValueError): validate_identity('someone@example.org', SEED)

def test_leakage_protection():
    frame = pd.read_csv(ROOT / 'data/AI_A2_2527343.csv')
    frame['yield_per_hectare'] = frame.yield_tons / frame.field_size_ha
    assert feature_frame(frame).columns.tolist() == FEATURES
    for model in Predictor().models.values():
        assert list(model.feature_names_in_) == FEATURES
        assert set(model.feature_names_in_).isdisjoint({'yield_tons', 'high_risk', 'yield_per_hectare'})

def test_train_only_imputation():
    from sklearn.model_selection import train_test_split
    clean, _ = validate_data(pd.read_csv(ROOT / 'data/AI_A2_2527343.csv'))
    train, test = train_test_split(clean, test_size=.25, random_state=SEED, stratify=clean.high_risk)
    from src.config import NUMERIC
    for model in Predictor().models.values():
        imputer = model.named_steps['preprocess'].named_transformers_['numeric'].named_steps['impute']
        np.testing.assert_allclose(imputer.statistics_, train[NUMERIC].median().to_numpy())
    assert set(train.index).isdisjoint(test.index)

def test_quality_rejects_bad_range():
    frame = pd.read_csv(ROOT / 'data/AI_A2_2527343.csv')
    frame.loc[0, 'field_size_ha'] = 0
    with pytest.raises(ValueError, match='field_size_ha'): validate_data(frame)

def test_api_contract(valid):
    with TestClient(app) as client:
        assert client.get('/health').json() == {'status': 'ok', 'models_ready': True}
        assert client.get('/model-info').json()['verification_code'] == CODE
        response = client.post('/predict', json=valid)
        assert response.status_code == 200
        assert response.json() == Predictor().predict(FarmRecord(**valid))
        assert client.get('/docs').status_code == 200

@pytest.mark.parametrize('payload', [{}, {'rainfall_mm': 1600}, {'season': 'C'}])
def test_api_invalid(payload):
    with TestClient(app) as client:
        response = client.post('/predict', json=payload)
        assert response.status_code == 422 and 'detail' in response.json()

def test_malformed_json():
    with TestClient(app) as client:
        assert client.post('/predict', content='{bad', headers={'Content-Type': 'application/json'}).status_code == 422

@pytest.mark.parametrize('field,value', [('rainfall_mm', 1500), ('avg_temp_c', 'warm'), ('season', 'C'), ('cooperative_support', True), ('soil_moisture_pct', None)])
def test_api_field_errors(valid, field, value):
    valid[field] = value
    with TestClient(app) as client:
        response = client.post('/predict', json=valid)
        assert response.status_code == 422
        assert any(field in error['loc'] for error in response.json()['detail'])

def test_unavailable_models(valid):
    with TestClient(app) as client:
        app.state.predictor = None
        assert client.get('/health').json()['models_ready'] is False
        assert client.get('/model-info').status_code == 503
        assert client.post('/predict', json=valid).status_code == 503

def test_cli(valid):
    good = subprocess.run([sys.executable, str(ROOT / 'predict.py'), '--json', str(ROOT / 'samples/valid.json')], capture_output=True, text=True)
    assert good.returncode == 0 and json.loads(good.stdout)['verification_code'] == CODE
    bad = subprocess.run([sys.executable, str(ROOT / 'predict.py'), '--json', str(ROOT / 'samples/invalid.json')], capture_output=True, text=True)
    assert bad.returncode != 0 and 'Input/model error' in bad.stderr

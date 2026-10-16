"""FastAPI serving trusted saved pipelines, with no request-time training."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.validation import FarmRecord
from src.inference import Predictor

@asynccontextmanager
async def lifespan(app):
    """Load once at service startup, keeping health available if artifacts lack."""
    app.state.predictor = None
    try:
        app.state.predictor = Predictor()
    except (OSError, ValueError):
        pass
    yield

app = FastAPI(title='Musanze Harvest Intelligence Service', version='1.0', lifespan=lifespan)

def ready():
    """Return loaded models or an explicit service-unavailable response."""
    predictor = getattr(app.state, 'predictor', None)
    if predictor is None:
        raise HTTPException(503, 'Models unavailable. Run run_all.py before starting the service.')
    return predictor

class Prediction(BaseModel):
    """Validated response contract."""
    predicted_yield_tons: float
    predicted_high_risk: int
    high_risk_probability: float
    cluster: int
    verification_code: str

@app.get('/health')
def health():
    """Expose service status and saved-model readiness."""
    loaded = getattr(app.state, 'predictor', None) is not None
    return {'status': 'ok' if loaded else 'degraded', 'models_ready': loaded}

@app.get('/model-info')
def model_info():
    """Expose feature contract and reproducibility signature."""
    return ready().info

@app.post('/predict', response_model=Prediction)
def predict(record: FarmRecord):
    """Predict harvest, risk and cluster for a bounded validated record."""
    return ready().predict(record)

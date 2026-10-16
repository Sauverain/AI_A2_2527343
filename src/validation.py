"""Shared inference schema and dataset quality controls."""
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from typing import Literal
from src.config import FEATURES, TARGETS, BOUNDS

class FarmRecord(BaseModel):
    """Prediction-time measurements; targets and unknown fields are forbidden."""
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)
    rainfall_mm: float = Field(ge=600, le=1400)
    avg_temp_c: float = Field(ge=12, le=26)
    soil_moisture_pct: float = Field(ge=20, le=80)
    fertilizer_kg: float = Field(ge=0, le=250)
    field_size_ha: float = Field(ge=.2, le=4)
    season: Literal['A', 'B']
    cooperative_support: StrictInt = Field(ge=0, le=1)

def feature_frame(frame):
    """Whitelist measured inputs, never inferred target-derived columns."""
    return frame.loc[:, FEATURES].copy()

def validate_data(frame):
    """Validate raw schema and ranges, permitting only deliberate missingness."""
    if set(frame.columns) != set(FEATURES + TARGETS):
        raise ValueError('Dataset columns do not match the required schema')
    for column, (lo, hi) in BOUNDS.items():
        values = frame[column]
        if not pd.api.types.is_numeric_dtype(values):
            raise ValueError(f'{column}: numeric values required')
        if not values.dropna().between(lo, hi).all():
            raise ValueError(f'{column}: values must be between {lo} and {hi}')
        if column not in ['soil_moisture_pct', 'fertilizer_kg'] and values.isna().any():
            raise ValueError(f'{column}: missing values forbidden')
    if not frame.season.isin(['A', 'B']).all() or not frame.cooperative_support.isin([0, 1]).all():
        raise ValueError('Invalid categorical value')
    if not frame.high_risk.isin([0, 1]).all() or not np.isfinite(frame.yield_tons).all() or not frame.yield_tons.ge(.5).all():
        raise ValueError('Invalid targets')
    clean = frame.drop_duplicates().copy()
    return clean, {'raw_rows': len(frame), 'clean_rows': len(clean),
        'duplicate_rows': int(frame.duplicated().sum()),
        'missing_raw': frame.isna().sum().to_dict(), 'missing_clean': clean.isna().sum().to_dict()}

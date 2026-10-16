"""Reusable train-only numeric and categorical transformations."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from src.config import NUMERIC

def preprocessor():
    """Return a new, unfitted transformer for each candidate model."""
    return ColumnTransformer([
        ('numeric', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), NUMERIC),
        ('season', OneHotEncoder(handle_unknown='error', sparse_output=False), ['season'])])

def pipeline(estimator):
    """Bundle preprocessing and model to guarantee identical inference."""
    return Pipeline([('preprocess', preprocessor()), ('model', estimator)])

"""Regression candidate definitions."""
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from src.config import SEED

def candidates():
    """Return fixed, reproducible candidates without test-set tuning."""
    return {'DummyRegressor': DummyRegressor(strategy='mean'), 'LinearRegression': LinearRegression(),
        'RandomForestRegressor': RandomForestRegressor(n_estimators=200, random_state=SEED, n_jobs=1)}

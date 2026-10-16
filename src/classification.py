"""Classification candidate definitions."""
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from src.config import SEED

def candidates():
    """Return majority baseline and two fixed classifiers."""
    return {'DummyClassifier': DummyClassifier(strategy='most_frequent'),
        'LogisticRegression': LogisticRegression(max_iter=2000, random_state=SEED),
        'RandomForestClassifier': RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=1)}

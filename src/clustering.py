"""Train feature-only KMeans and produce measured cluster profiles."""
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from src.preprocessing import pipeline
from src.config import SEED, NUMERIC

def train_clusters(train):
    """Fit K=2..6 on training inputs; choose maximum training silhouette."""
    models, scores = {}, {}
    for k in range(2, 7):
        model = pipeline(KMeans(n_clusters=k, random_state=SEED, n_init=20))
        labels = model.fit_predict(train)
        scores[str(k)] = float(silhouette_score(model.named_steps['preprocess'].transform(train), labels))
        models[k] = model
    best = max(range(2, 7), key=lambda k: scores[str(k)])
    selected = models[best]
    profiled = train.copy()
    profiled['cluster'] = selected.predict(train)
    profiles = {}
    for label, group in profiled.groupby('cluster'):
        means = group[NUMERIC].mean().to_dict()
        profiles[str(label)] = {'size': len(group), 'means_observed': means,
            'season_A_fraction': float((group.season == 'A').mean()),
            'interpretation': f"Training group {label}: {len(group)} farms; mean rainfall {means['rainfall_mm']:.1f} mm, temperature {means['avg_temp_c']:.1f} C, field size {means['field_size_ha']:.2f} ha and support fraction {means['cooperative_support']:.2f}. Use these measured similarities for field-visit planning, subject to officer review."}
    return selected, {'scores': scores, 'selected_k': best, 'selection_reason': 'Maximum silhouette on scaled training inputs; no targets used.', 'profiles': profiles, 'profile_scope': 'Training farms; numeric means exclude missing measurements.'}

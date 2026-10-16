"""Measured held-out metrics and JSON serialization."""
import json
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

def write_json(path, value):
    """Write standards-compliant, readable evidence."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def regression_metrics(actual, predicted):
    """Return regression test metrics in tons and dimensionless R squared."""
    return {'mae': mean_absolute_error(actual, predicted), 'rmse': float(np.sqrt(mean_squared_error(actual, predicted))), 'r2': r2_score(actual, predicted)}

def classification_metrics(actual, predicted, probability):
    """Return positive-class metrics; AUC is null for a single-class sample."""
    return {'precision': precision_score(actual, predicted, zero_division=0),
        'recall': recall_score(actual, predicted, zero_division=0), 'f1': f1_score(actual, predicted, zero_division=0),
        'confusion_matrix': confusion_matrix(actual, predicted, labels=[0, 1]).tolist(),
        'roc_auc': roc_auc_score(actual, probability) if len(np.unique(actual)) == 2 else None}

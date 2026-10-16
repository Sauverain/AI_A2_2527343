"""Single-command reproducible training and artifact generation."""
import argparse
import os
import tempfile
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'musanze_mpl_2527343'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.metrics import ConfusionMatrixDisplay
from data.generate_data import generate_data
from src.config import ROOT, SEED, CODE, FEATURES, validate_identity
from src.validation import validate_data, feature_frame
from src.preprocessing import pipeline
from src.regression import candidates as regressors
from src.classification import candidates as classifiers
from src.clustering import train_clusters
from src.evaluation import write_json, regression_metrics, classification_metrics

def run(student_id, seed):
    """Validate signature, regenerate data and fit all transformers on train only."""
    validate_identity(student_id, seed)
    for folder in ['artifacts/plots', 'models', 'docs', 'evidence']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    raw, digest = generate_data()
    clean, quality = validate_data(raw)
    train, test = train_test_split(clean, test_size=.25, random_state=SEED, stratify=clean.high_risk)
    xtrain, xtest = feature_frame(train), feature_frame(test)
    quality.update(train_rows=len(train), test_rows=len(test), split='75/25 stratified high_risk; random_state=7343', row_id='zero-based original CSV data-row position')
    write_json(ROOT / 'artifacts/data_quality.json', quality)
    results, fitted = {}, {}
    for task, candidates, target in [('regression', regressors(), 'yield_tons'), ('classification', classifiers(), 'high_risk')]:
        scores, models = {}, {}
        for name, estimator in candidates.items():
            model = pipeline(estimator).fit(xtrain, train[target])
            pred = model.predict(xtest)
            scores[name] = regression_metrics(test[target], pred) if task == 'regression' else classification_metrics(test[target], pred, model.predict_proba(xtest)[:, 1])
            models[name] = model
        best = min(scores, key=lambda n: scores[n]['rmse']) if task == 'regression' else max(scores, key=lambda n: (scores[n]['f1'], scores[n]['recall']))
        results[task] = {'verification_code': CODE, 'seed': SEED, 'candidates': scores, 'selected_model': best, 'selected_metrics': scores[best],
            'selection_reason': 'Lowest held-out RMSE.' if task == 'regression' else 'Highest held-out positive-class F1; recall breaks ties.',
            'selection_limitation': 'Selection uses this test split as assignment permits; an independent external evaluation is still needed.'}
        fitted[task] = models[best]
        joblib.dump(models[best], ROOT / f'models/{task}.joblib')
        write_json(ROOT / f'artifacts/{task}_metrics.json', results[task])
    cluster, report = train_clusters(xtrain)
    report.update(seed=SEED, verification_code=CODE)
    write_json(ROOT / 'artifacts/clustering_report.json', report)
    joblib.dump(cluster, ROOT / 'models/clustering.joblib')
    info = {'verification_code': CODE, 'seed': SEED, 'features': FEATURES, 'selected_k': report['selected_k'],
        'regression': results['regression']['selected_model'], 'classification': results['classification']['selected_model'],
        'dataset_sha256': digest, 'synthetic_data': True, 'decision_threshold': .5}
    write_json(ROOT / 'models/model_info.json', info)
    out = pd.DataFrame({'row_id': test.index, 'actual_yield_tons': test.yield_tons,
        'predicted_yield_tons': fitted['regression'].predict(xtest), 'actual_high_risk': test.high_risk,
        'predicted_high_risk': fitted['classification'].predict(xtest),
        'high_risk_probability': fitted['classification'].predict_proba(xtest)[:, 1], 'cluster': cluster.predict(xtest)})
    out['yield_error_pred_minus_actual'] = out.predicted_yield_tons - out.actual_yield_tons
    out['classification_error'] = (out.predicted_high_risk != out.actual_high_risk).astype(int)
    out.to_csv(ROOT / 'artifacts/test_predictions.csv', index=False, float_format='%.10f', lineterminator='\n')
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.scatter(out.predicted_yield_tons, -out.yield_error_pred_minus_actual, alpha=.75)
    ax.axhline(0, color='black', linewidth=1)
    ax.set(xlabel='Predicted harvest (tons)', ylabel='Actual - predicted (tons)', title='Held-out regression residuals')
    fig.tight_layout(); fig.savefig(ROOT / 'artifacts/plots/residuals.png', dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(4.5, 3.4))
    ConfusionMatrixDisplay.from_predictions(out.actual_high_risk, out.predicted_high_risk, display_labels=['Lower risk', 'High risk'], ax=ax, colorbar=False)
    ax.set_title('Held-out risk classification'); fig.tight_layout(); fig.savefig(ROOT / 'artifacts/plots/confusion_matrix.png', dpi=150); plt.close(fig)
    transformed = cluster.named_steps['preprocess'].transform(xtrain)
    pca = PCA(n_components=2, svd_solver='full').fit(transformed)
    xy = pca.transform(transformed)
    fig, ax = plt.subplots(figsize=(6, 3.4))
    labels = cluster.predict(xtrain)
    for c in range(report['selected_k']):
        ax.scatter(xy[labels == c, 0], xy[labels == c, 1], label=f'Cluster {c}', alpha=.7, s=20)
    ax.set(xlabel=f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', ylabel=f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', title='Training farm clusters: PCA projection')
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(ROOT / 'artifacts/plots/clusters.png', dpi=150); plt.close(fig)
    write_json(ROOT / 'artifacts/projection.json', {'method': 'PCA, training features only', 'explained_variance_ratio': pca.explained_variance_ratio_.tolist()})
    print(CODE, '\nSHA-256:', digest)
    for task, result in results.items():
        print(task, result['selected_model'], result['selected_metrics'])
    print('Selected K:', report['selected_k'], 'Silhouettes:', report['scores'])
    print('Rows:', quality)
    print('Generated artifacts:', ', '.join(str(p.relative_to(ROOT)) for folder in ['artifacts', 'models'] for p in sorted((ROOT / folder).rglob('*')) if p.is_file()))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--student-id', required=True)
    parser.add_argument('--seed', required=True, type=int)
    args = parser.parse_args()
    try:
        run(args.student_id, args.seed)
    except ValueError as exc:
        parser.exit(2, f'Error: {exc}\n')

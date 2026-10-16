# Alain Sauverain ISHEMA

Registration: **25/27343** | Institutional username: **ug2527343@ines.ac.rw** | **AI-A2-7343**

INES Ruhengeri — SWE 3513 Artificial Intelligence — Individual Assignment 2

Musanze Harvest Intelligence Service estimates harvest tons, predicts below-median synthetic productivity risk, and groups similar farms for cooperative planning. **All data is synthetic.** This classroom prototype requires field-officer and agronomist review and must not determine access to finance, insurance or public services.

## Setup and reproduce

Tested: Python 3.10.6, Windows 10. Exact tested dependencies are pinned in requirements.txt. A clean project-local virtual environment was used.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_all.py --student-id ug2527343@ines.ac.rw --seed 7343
python predict.py --json samples/valid.json
python predict.py --json samples/invalid.json
pytest -q
uvicorn app:app --host 127.0.0.1 --port 8000
```

The invalid CLI command intentionally exits 2. Training needs no network after setup. Run from the project root. On Linux/macOS use `source .venv/bin/activate`.

`python tools/verify.py` runs the full pipeline twice, compares artifact bytes, executes valid/invalid CLI checks and pytest, and saves actual API responses. `python tools/build_docs.py` regenerates the report, unsigned declaration and supporting documents from those measurements. It overwrites generated drafts; preserve your personal edits first. `python tools/package.py` validates and builds the ZIP without environments, Git internals or caches.

## Dataset and models

244 base rows, 247 raw rows, 244 after duplicate removal. Seed 7343; training/testing 183/61. Missing predictors remain in CSV and are imputed with training medians. Explicit input whitelist excludes both targets and yield/ha. Pipelines contain the fitted numeric imputer/scaler, season encoder and estimator. SHA-256: `19a1558643adbce326107d7fcfb9df4a8cd48cf745f2af43b8e07af6b6975d62`.

Regression: LinearRegression, selected by lowest test RMSE. Classification: LogisticRegression, selected by highest test F1. KMeans: K=2, maximum training silhouette. Comparison tables and actual errors appear in the report and JSONs. Test selection is permitted by the assignment but needs a fresh external evaluation before deployment. Probability calibration and prediction intervals are not established.

## API

Open http://127.0.0.1:8000/docs. GET /health reports status/readiness. GET /model-info includes seed, code, features, models and K. POST /predict accepts the seven inputs in samples/valid.json. It returns predicted_yield_tons, predicted_high_risk, high_risk_probability, cluster and verification_code. No models are trained during requests. Missing artifacts produce degraded health and HTTP 503 for inference.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/model-info
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType application/json -Body (Get-Content samples/valid.json -Raw)
```

Strict shared Pydantic schema rejects missing/extra fields, wrong types, numeric strings, nonfinite values, invalid seasons and values outside generation bounds. API errors are HTTP 422 with field details; malformed JSON also returns 422. Support must be integer 0 or 1. Integer JSON measurements are accepted as numbers. The service is local and unauthenticated; joblib artifacts must be trusted.

## Structure and evidence

- data/generate_data.py and data/AI_A2_2527343.csv: deterministic generator and corrupted synthetic CSV.
- src/: configuration, validation, preprocessing, separate model candidates, clustering, metrics and shared inference.
- models/: three complete saved pipelines plus model_info.json.
- artifacts/: fingerprint, data quality, regression/classification metrics, cluster report, PCA variance, held-out prediction CSV, residuals/confusion matrix/cluster plots.
- tests/: meaningful integration and failure-path tests. Actual latest summary: **28 passed, 1 warning in 17.36s**.
- docs/AI_A2_2527343_REPORT.pdf: seven-page technical report; PERSONAL_REVIEW.md: required personal interpretation worksheet.
- evidence/: actual command/API/reproducibility captures, PDF test log, unsigned declaration, AI disclosure and recording checklist.

Row IDs are zero-based CSV data-row positions before deduplication. CSV regression error = predicted minus actual; plot residual = actual minus predicted. Cluster profiles describe training farms; observed means omit missing measurements. All K scores and confusion matrices are in JSON. Extra tools: httpx supports TestClient; reportlab generates PDFs; pypdf and PyMuPDF verify PDF page count and rendering. pytest is for automated checks; uvicorn serves the API.

## Submission status and repository

**PROVISIONAL**: authentic continuous unedited <=2-minute video, signature, and personally rewritten error/cluster interpretations are pending. Review AI_USE.md and the declaration for truthfulness. No personal reflection or video is claimed complete. Deadline: 19 October 2026, 5:00 PM CAT; Moodle timestamp is authoritative.

Repository URL: no remote configured at preparation time. Obtain the real current commit using `git log -1 --format=%H`; the package's evidence/FINAL_COMMIT.txt records the packaged implementation commit. A commit cannot embed its own hash in its tracked README. After personal edits, commit again and record the final hash for the video.

```powershell
git remote add origin <YOUR_ACTUAL_GITHUB_REPOSITORY_URL>
git push -u origin HEAD
```

Create the repository in your own account first; replace the placeholder with its actual URL. No remote was invented or pushed. Complete personal evidence, regenerate documentation as appropriate, run verification, commit changes, record the authentic video using that hash, rebuild and inspect the ZIP, then upload AI_A2_2527343.zip to INES e-learning before the deadline.

## Understanding and defense

The seed fixes the random sequence, and SHA-256 checks CSV bytes. Deduplication prevents identical copies crossing the split. Training-only medians/scaling prevent test distribution from influencing fitted transformations. Pipelines make saved inference match training. The mean and majority baselines show whether learning helps. RMSE penalizes large harvest errors; F1 balances precision/recall, while a missed risky farm may warrant special review. Silhouette compares feature cohesion and separation; a cluster is not a risk label. Read PERSONAL_REVIEW.md and explain one actual error and cluster in your own words. To change a field bound, update the shared schema and dataset bounds together and test valid/invalid boundary records.

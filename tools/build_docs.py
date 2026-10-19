"""Build seven-page evidence-based report and unsigned personal documents."""
import argparse
import json
import re
import platform
import sys
from pathlib import Path
from xml.sax.saxutils import escape
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from src.config import ROOT, NAME, CODE, STUDENT_ID, BOUNDS

S = getSampleStyleSheet()
S.add(ParagraphStyle(name='SmallText', parent=S['BodyText'], fontSize=9, leading=12, spaceAfter=5))
S['BodyText'].fontSize = 10
S['BodyText'].leading = 14
S['BodyText'].spaceAfter = 7
S['Heading1'].fontSize = 19
S['Heading1'].textColor = colors.HexColor('#123e50')
S['Heading2'].fontSize = 12

def p(text, small=False):
    return Paragraph(escape(str(text)).replace('\n', '<br/>'), S['SmallText' if small else 'BodyText'])

def table(rows, widths=None):
    t = Table([[p(c, True) for c in row] for row in rows], colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND', (0,0),(-1,0),colors.HexColor('#e1edf1')), ('VALIGN',(0,0),(-1,-1),'TOP'), ('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#123e50')), ('BOTTOMPADDING',(0,0),(-1,-1),5), ('TOPPADDING',(0,0),(-1,-1),5), ('GRID',(0,1),(-1,-1),.2,colors.lightgrey)]))
    return t

def footer(canvas, doc):
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#365762'))
    canvas.drawString(42, 25, f'INES Ruhengeri | SWE 3513 | {CODE} | 25/27343')
    canvas.drawRightString(A4[0]-42, 25, str(doc.page))

def pdf(path, story):
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=42, leftMargin=42, topMargin=37, bottomMargin=42, title=path.stem, author=NAME).build(story, onFirstPage=footer, onLaterPages=footer)

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def main(report_only=False):
    """Generate documentation from saved measurements, never estimated results."""
    reg, clf, cluster = [load('artifacts/' + n) for n in ['regression_metrics.json','classification_metrics.json','clustering_report.json']]
    quality = load('artifacts/data_quality.json')
    digest = (ROOT / 'artifacts/data_fingerprint.txt').read_text().strip()
    runs = load('evidence/execution_log.json')
    pytest_run = next(x for x in runs if '-m pytest' in x['command'])
    test_summary = pytest_run['stdout'].strip().splitlines()[-1]
    preds = pd.read_csv(ROOT / 'artifacts/test_predictions.csv')
    error = preds.loc[preds.yield_error_pred_minus_actual.abs().idxmax()]
    errors = preds[preds.classification_error == 1]
    ce = errors.iloc[0] if len(errors) else None
    regression_note = f"CSV row {int(error.row_id)}: actual {error.actual_yield_tons:.4f} tons; predicted {error.predicted_yield_tons:.4f}; predicted minus actual {error.yield_error_pred_minus_actual:.4f} tons. This is the largest absolute test error. Such an error could distort transport and storage planning. Missing measurements, noise and the linear model's inability to represent the temperature kink are plausible contributors, not a proven explanation for this row."
    classification_note = (f"CSV row {int(ce.row_id)}: actual risk {int(ce.actual_high_risk)}, predicted {int(ce.predicted_high_risk)}, probability {ce.high_risk_probability:.4f}. " + ('This false negative could cause a field officer to overlook a farm needing assessment.' if ce.actual_high_risk == 1 else 'This false positive could divert field visits to a farm outside the synthetic high-risk class.')) if ce is not None else 'No held-out classification errors occurred; no error example can honestly be invented.'
    cluster_note = next(iter(cluster['profiles'].values()))['interpretation']
    review = f"""# Personal interpretation worksheet — AI-assisted draft

Alain Sauverain ISHEMA | 25/27343 | ug2527343@ines.ac.rw | AI-A2-7343

The assignment requires your own interpretations. The factual examples below were generated from artifacts; they are not presented as your personal reflections. Check the row values in artifacts/test_predictions.csv, rewrite each explanation in your own words, and update the report using tools/build_docs.py or edit its source text after understanding it.

## Regression evidence
{regression_note}

Your interpretation: [write what the signed error means, why it matters locally, and what additional measurement you would check]

## Classification evidence
{classification_note}

Your interpretation: [explain the practical cost of this actual error and the role of human review]

## Cluster evidence
{cluster_note}

Your interpretation: [describe a useful cooperative action and why a cluster is not a risk label]

## Reflection
[Explain what you personally learned, what you checked, and one change you can defend. Do not sign the declaration until it is accurate.]
"""
    review_path = ROOT / 'docs/PERSONAL_REVIEW.md'
    if not review_path.exists():
        review_path.write_text(review, encoding='utf-8')
    reviewed = review_path.read_text(encoding='utf-8')
    sections = {}
    for number, title in enumerate(['Regression Interpretation', 'Classification Interpretation', 'Clustering Interpretation', 'Personal Reflection'], 1):
        match = re.search(r'^## ' + str(number) + r'\. ' + title + r'\s*\n(.*?)(?=^## |\Z)', reviewed, re.M | re.S)
        if not match or not match.group(1).strip():
            raise ValueError(f'Missing reviewed section: {title}')
        sections[title] = [text.strip() for text in match.group(1).strip().split('\n\n') if text.strip()]
    story = []
    def page(title, content):
        if story: story.append(PageBreak())
        story.append(Paragraph(title, S['Heading1']))
        story.extend(content)
    page('1. Identity and decision problem', [p('Musanze Harvest Intelligence Service'),
        table([['Identity', 'Confirmed details'], ['Full name', NAME], ['Registration / email', '25/27343 / ' + STUDENT_ID], ['Institution / course', 'INES Ruhengeri / SWE 3513 - Artificial Intelligence'], ['Assessment / signature', 'Individual Assignment 2 / ' + CODE], ['Deadline', '19 October 2026, 5:00 PM CAT']],[140,371]),
        Spacer(1,14), p('A Musanze potato cooperative needs to consolidate inconsistent farm records into estimates that support harvest collection and field visits. The field officer remains the decision maker.'),
        table([['Task', 'Question and output'], ['Regression', 'How many tons will this farm harvest? Output: predicted_yield_tons.'], ['Classification', 'Is synthetic yield per hectare below the base-data median? Output: high-risk label and probability.'], ['Clustering', 'Which farms have similar measured conditions? Output: cluster membership.']],[90,421]),
        Paragraph('Ethical boundary', S['Heading2']), p('This is a classroom prototype trained entirely on synthetic data. It must not replace an agronomist or decide access to finance, insurance or public services. A high-risk label is a dataset definition, not a diagnosis of crop disease or a verified forecast of farm failure.'),
        p('AI-assisted implementation and draft explanations are disclosed in evidence/AI_USE.md. The interpretations and reflection in this report are taken from docs/PERSONAL_REVIEW.md, which the student confirmed as completed and reviewed. No signature or authentic demonstration is certified by this report update.')])
    dictionary = [['Column', 'Meaning / range']]+[[k, f'{a} to {b}; '+('binary' if k=='cooperative_support' else 'numeric')] for k,(a,b) in BOUNDS.items()]+[['season','A or B'],['yield_tons','Synthetic harvest target; minimum 0.50 tons'],['high_risk','1 if pre-missingness yield/ha is below base median; otherwise 0']]
    page('2. Data and reproducibility', [table(dictionary,[155,356]), Spacer(1,9),
        p('Seed = last four registration digits = 7343. numpy.random.default_rng(7343); base rows = 240 + (7343 % 41) = 244. Labels are created before missingness, using unrounded generated values. The median is part of the specified synthetic label generator, not a fitted prediction-time feature.'),
        p('Yield = 0.004 rainfall + 0.06 moisture + 0.02 fertilizer + 1.30 field size - 0.25 abs(temperature - 18) + 0.70 support + season effect + N(0, 0.80). Season A adds 0.50; B subtracts 0.20. Clip at 0.50.'),
        p(f"Raw rows {quality['raw_rows']}; duplicates {quality['duplicate_rows']}; cleaned rows {quality['clean_rows']}. Exactly 12 unique positions per missingness column are sampled separately (overlap is allowed). The first three corrupted records are appended as exact duplicates. Clean missing counts: moisture {quality['missing_clean']['soil_moisture_pct']}, fertilizer {quality['missing_clean']['fertilizer_kg']}; raw counts: moisture {quality['missing_raw']['soil_moisture_pct']}, fertilizer {quality['missing_raw']['fertilizer_kg']}."),
        p('CSV floats have four decimals; UTF-8 with explicit LF line endings. SHA-256 hashes final CSV bytes:'), p(digest[:32]+'\n'+digest[32:]), p('Two complete pipeline executions produced identical CSV fingerprint, metric JSON files, cluster report and test-prediction CSV bytes. See evidence/reproducibility.json. Missing predictors are preserved until training-only median imputation.')])
    page('3. Pipeline design and leakage controls', [p(f"After removing duplicate records, a fixed stratified 75/25 split produces {quality['train_rows']} training and {quality['test_rows']} testing farms; random_state=7343. Original zero-based CSV positions remain row IDs. Duplicate removal precedes the split so copies cannot appear on opposite sides."),
        table([['Stage','Transformation / control'],['Raw CSV -> validation','Exact schema, numeric bounds, categorical values, missingness and duplicate evidence.'],['Clean -> split','No imputation, scaling or encoding is fitted before splitting.'],['Numeric branch','Training medians -> StandardScaler fitted on training inputs. Binary support is scaled with other numeric inputs.'],['Season branch','OneHotEncoder fitted on training season values; inference accepts A/B only.'],['Model -> saved pipeline','Each candidate has an independent ColumnTransformer. Final joblib pipelines retain their fitted transformers.']],[120,391]), Spacer(1,12),
        p('Only rainfall, temperature, moisture, fertilizer, field size, cooperative support and season are inputs. An explicit whitelist excludes yield_tons, high_risk and any yield-per-hectare column. Clustering uses the same measured-input whitelist and training farms only.'),
        p('Regression candidates: mean DummyRegressor, LinearRegression, and RandomForestRegressor (200 trees). Classification: most-frequent DummyClassifier, LogisticRegression and RandomForestClassifier (200 trees). Forests use one worker; random states are fixed. KMeans tests K=2..6 with n_init=20.'),
        p('Selection uses lowest test RMSE for regression and highest test F1 for classification (recall breaks ties). The PDF permits selection on test evidence, but this makes the selected score optimistic as an estimate of future performance. Future work should use train/validation selection and a separate untouched test set.'),
        p('Training -> artifacts/models -> shared Predictor -> CLI and FastAPI. Inference never retrains; the API loads saved trusted pipelines at startup. Tests verify stored imputer medians against training medians and confirm feature exclusion.')])
    rt = [['Regressor','MAE','RMSE','R squared']]+[[n, f"{m['mae']:.4f}",f"{m['rmse']:.4f}",f"{m['r2']:.4f}"] for n,m in reg['candidates'].items()]
    ct = [['Classifier','Precision','Recall','F1','ROC-AUC']]+[[n]+[f"{m[k]:.4f}" if m[k] is not None else 'N/A' for k in ['precision','recall','f1','roc_auc']] for n,m in clf['candidates'].items()]
    page('4. Regression and classification', [table(rt,[185,105,105,116]), Spacer(1,5), table(ct,[175,84,84,84,84]),
        p(f"Selected: {reg['selected_model']} (lowest RMSE); {clf['selected_model']} (highest F1). Positive class = 1, probability threshold = 0.5. All candidates share the same held-out farms.",True),
        Table([[Image(str(ROOT/'artifacts/plots/residuals.png'),width=267,height=151),Image(str(ROOT/'artifacts/plots/confusion_matrix.png'),width=224,height=169)]]),
        p('Residual sign in the plot is actual minus predicted; the CSV uses predicted minus actual. Confusion-matrix rows are actual classes, columns predicted classes. ROC-AUC uses probabilities and is reported only with both true classes.',True),
        *[p(text,True) for text in sections['Regression Interpretation']],
        *[p(text,True) for text in sections['Classification Interpretation']],
        p('High risk here means below-median synthetic yield per hectare, not a verified crop-failure event.',True)])
    page('5. Clustering and operational meaning', [table([['K','Training silhouette']]+[[k,f'{v:.5f}'] for k,v in cluster['scores'].items()],[100,411]),
        p(f"Selected K={cluster['selected_k']} maximizes silhouette among the five candidates. The low best score ({max(cluster['scores'].values()):.3f}) indicates weak separation. Here the groups split exactly by cooperative support; other mean conditions are similar. Silhouette does not establish agronomic validity. Cluster IDs are arbitrary; no target enters fitting."),
        Image(str(ROOT/'artifacts/plots/clusters.png'),width=440,height=249),
        p('The PCA projection is fitted on training inputs; axes show the explained variance of each principal component. Separation in two dimensions may conceal overlap in the full feature space.',True),
        *[p(v['interpretation'],True) for v in cluster['profiles'].values()],
        p('Profiles use observed numeric means (missing measurements omitted) and include season proportions in the JSON. They do not identify causal interventions.',True),
        *[p(text,True) for text in sections['Clustering Interpretation']]])
    page('6. API contract and actual testing', [table([['Endpoint','Contract'],['GET /health','200: status and models_ready. Missing artifacts produce degraded health.'],['GET /model-info','200: selected models, features, K, seed, verification code and fingerprint; 503 if unavailable.'],['POST /predict','Seven required bounded fields -> yield, risk label, probability, cluster and verification code. Invalid input -> 422 with field details; unavailable models -> 503.'],['GET /docs','Swagger UI; /openapi.json describes typed request and response.']],[135,376]),
        p('Valid request: '+(ROOT/'samples/valid.json').read_text(),True),
        p('Actual CLI response: '+next(x['stdout'] for x in runs if x['command']=='python predict.py --json samples/valid.json'),True),
        p('Invalid sample combines rainfall 1500, temperature "warm" and season C. CLI returned exit 2 with validation details. API tests exercise missing fields, invalid values and malformed JSON (HTTP 422). Numeric strings, boolean support, NaN and extra target fields are rejected by shared strict Pydantic validation.',True),
        Paragraph('Executed evidence',S['Heading2']), p(test_summary),
        p('pytest checks valid inference, missing/type/range/season/extra/nonfinite failures, reproducible bytes, 247/244 row counts, 12 missing values per cleaned column, signature, saved model loading, wrong seed rejection, leakage controls, train-only imputation, CLI behavior and FastAPI responses. Full raw stdout/stderr is in evidence/execution_log.json.'),
        p('FastAPI TestClient verified health, model-info, docs, valid prediction, missing-field validation and malformed JSON. Explicit endpoint responses are saved in evidence/api_checks.json. No authentic video or student signature is claimed. No live browser interaction, load test or real agricultural validation is claimed here.')])
    page('7. Responsible AI model card', [table([['Aspect','Scope and limitation'],['Intended user / use','Cooperative field officers; classroom harvest planning and prioritization support.'],['Data provenance','244 synthetic base farms. No actual farm measurements, farmer identities or consented field outcomes.'],['Target meaning','High risk means below-median synthetic tons/ha, not disease, poverty or an independently validated failure event.'],['Performance scope','One fixed split. Test evidence is also used for model selection. Small sample and random missingness constrain reliability.'],['Risks','Overconfident estimates, unfair service allocation, synthetic correlations, measurement errors and failure under distribution shift.'],['Prohibited use','Automatic finance, insurance or public-service access decisions; replacing an agronomist.'],['Human oversight','Confirm farm measurements, inspect uncertain cases and obtain agronomist advice before action. Avoid punitive interpretations of risk labels.'],['Security / privacy','No authentication or production rate limiting. Bind locally. Load only trusted joblib files, which can execute code. Collect minimal farmer data in any future deployment.']],[128,383]),
        Spacer(1,12), p('Improvement plan: gather representative real seasonal data with consent, verify measurement quality, use separate validation/test sets, test subgroup performance, quantify harvest uncertainty and calibrate risk probabilities. Compare richer temperature features under training-only cross-validation. Monitor drift and document retraining decisions.'),
        Paragraph('Personal reflection',S['Heading2']),
        *[p(text,True) for text in sections['Personal Reflection']],
        p('Source: supplied eight-page INES Ruhengeri SWE 3513 Individual Assignment 2 PDF, issued 16 October 2026. All numerical claims in this report are read from the accompanying generated artifacts.')])
    pdf(ROOT/'docs/AI_A2_2527343_REPORT.pdf', story)
    if report_only:
        print('Generated technical report only; personal worksheet and declaration preserved.')
        return
    log_story = [Paragraph('Executed test log', S['Heading1']),p(f'{NAME} | {STUDENT_ID} | {CODE}'),p('Actual subprocess captures from tools/verify.py. Expected nonzero validation exits count as successful rejection checks. No skipped or failed runs are hidden from this log.')]
    for run in runs:
        log_story += [Paragraph(escape(run['command']), S['Heading2']),p(f"Exit {run['exit_code']}; expected {run['expected_exit_code']}"),p(run['stdout'] or '[no stdout]',True),p(run['stderr'] or '[no stderr]',True)]
    log_story += [p('Reproducibility: exact byte equality for the fingerprint, metric JSONs, clustering report and prediction CSV across two full pipeline executions.'),p('The first 22-test run also passed, with one Starlette/httpx deprecation warning. Its raw captures are retained in initial_execution_log.json. The suite was then expanded and rerun. Initial Matplotlib cache warnings were fixed by selecting a writable temporary cache. No failed or skipped pytest tests occurred.'),p('Not performed: authentic personal recording, student signature, independent real-farm evaluation, production load testing and browser-driven manual Swagger interaction. API behavior was exercised with TestClient; this is not evidence of the student recording it.')]
    env = load('evidence/environment_check.json')
    log_story += [Paragraph('Environment verification',S['Heading2']),p(env['environment']),p(env['python']),p(env['platform'])]
    for check in env['commands']:
        log_story += [p(check['command'] + ' -> exit ' + str(check['exit_code'])),p(check['stdout'],True),p(check['stderr'] or '[no stderr]',True)]
    pdf(ROOT/'evidence/AI_A2_2527343_TEST_LOG.pdf',log_story)
    pdf(ROOT/'evidence/AI_A2_2527343_DECLARATION.pdf',[
        Paragraph('Authorship declaration - unsigned draft',S['Heading1']),p(f'{NAME}\nRegistration: 25/27343\nInstitutional email: {STUDENT_ID}\nINES Ruhengeri | SWE 3513 | Individual Assignment 2\n{CODE}'),
        p('This draft must be personally reviewed and amended before signature. It does not assert that the student independently wrote AI-generated code or has already reviewed, understood or defended the complete system.'),
        p('Disclosed assistance: OpenAI Codex generated substantial Python implementation, tests, documentation and packaging, and executed automated verification. The data and reported model metrics were computed by the supplied programs. AI-assisted interpretation drafts are identified for student rewriting; no personal reflection or demonstration video has been fabricated.'),
        p('Student confirmation to complete only when truthful: I have reviewed the submitted code and evidence, checked the reported results, rewritten required interpretations in my own words, and can explain and modify the system. I have disclosed assistance in evidence/AI_USE.md and will follow applicable course rules for AI use. My demonstration recording is authentic, continuous and unedited.'),
        p('Edits or additional assistance to disclose: ____________________________________\n________________________________________________________________'),
        Spacer(1,25),p('Student signature: __________________________    Date: __________________'),p('Status: UNSIGNED - personal review and authentic demonstration pending.')])
    (ROOT/'evidence/AI_USE.md').write_text(f'''# AI assistance disclosure

{NAME} | 25/27343 | {STUDENT_ID} | {CODE}

OpenAI Codex was asked to implement this project from the supplied assignment PDF. Codex generated substantial source code, automated tests, measured-result reporting, technical documentation and packaging scripts. Codex executed environment installation, training, CLI and API checks and pytest. Exact evidence is in execution_log.json, api_checks.json and reproducibility.json. All metrics are computed from the synthetic dataset; no real agricultural validation is claimed.

Error and cluster explanations are AI-assisted factual drafts. Required student interpretations and reflection must be personally rewritten and reviewed. The unsigned declaration must be checked and signed by the student. No video, voice, signature or personal learning reflection was fabricated. No additional AI tool is claimed. Student: add any assistance used after this draft and confirm compliance with course policy before submission.
''',encoding='utf-8')
    checklist = '''# Authentic demo checklist — video NOT yet supplied

Create evidence/AI_A2_2527343_DEMO.mp4 yourself. One continuous unedited MP4, maximum two minutes, your own voice. Rehearse beforehand; do not fake command results or splice recording. Keep text readable. Run the service beforehand in another terminal if useful.

- 0–12 s: Show handwritten card: Alain Sauverain ISHEMA, 25/27343, AI-A2-7343. Identify yourself in your own voice. Show terminal clock (`Get-Date`) and `git rev-parse HEAD`.
- 12–40 s: Execute `python run_all.py --student-id ug2527343@ines.ac.rw --seed 7343`; show fingerprint, metrics and artifact list.
- 40–55 s: Open one metric JSON and its plot; explain one result in your own words without reading a prepared script.
- 55–75 s: Run valid and invalid predict.py commands; show actual output and error.
- 75–100 s: Show http://127.0.0.1:8000/docs, health and a valid predict response plus a validation error.
- 100–120 s: Run `pytest -q`; show report, reviewed/signed declaration and terminal clock.

Before recording: understand the code and results, complete PERSONAL_REVIEW.md, sign the truthful declaration, use the final reviewed Git commit, prepare all windows, and time a rehearsal. If actual runtime exceeds this outline, adjust pacing while retaining the PDF's required evidence. Never speed up or edit the final continuous recording. After adding evidence, commit reviewed changes, use the new commit in the video, rebuild the ZIP, and verify contents.
'''
    (ROOT/'evidence/DEMO_CHECKLIST.md').write_text(checklist,encoding='utf-8')
    readme = f'''# Alain Sauverain ISHEMA

Registration: **25/27343** | Institutional username: **{STUDENT_ID}** | **{CODE}**

INES Ruhengeri — SWE 3513 Artificial Intelligence — Individual Assignment 2

Musanze Harvest Intelligence Service estimates harvest tons, predicts below-median synthetic productivity risk, and groups similar farms for cooperative planning. **All data is synthetic.** This classroom prototype requires field-officer and agronomist review and must not determine access to finance, insurance or public services.

## Setup and reproduce

Tested: Python {platform.python_version()}, {platform.system()} {platform.release()}. Exact tested dependencies are pinned in requirements.txt. A clean project-local virtual environment was used.

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python run_all.py --student-id {STUDENT_ID} --seed 7343
python predict.py --json samples/valid.json
python predict.py --json samples/invalid.json
pytest -q
uvicorn app:app --host 127.0.0.1 --port 8000
```

The invalid CLI command intentionally exits 2. Training needs no network after setup. Run from the project root. On Linux/macOS use `source .venv/bin/activate`.

`python tools/verify.py` runs the full pipeline twice, compares artifact bytes, executes valid/invalid CLI checks and pytest, and saves actual API responses. `python tools/build_docs.py` regenerates the report, unsigned declaration and supporting documents from those measurements. It overwrites generated drafts; preserve your personal edits first. `python tools/package.py` validates and builds the ZIP without environments, Git internals or caches.

## Dataset and models

244 base rows, 247 raw rows, 244 after duplicate removal. Seed 7343; training/testing {quality['train_rows']}/{quality['test_rows']}. Missing predictors remain in CSV and are imputed with training medians. Explicit input whitelist excludes both targets and yield/ha. Pipelines contain the fitted numeric imputer/scaler, season encoder and estimator. SHA-256: `{digest}`.

Regression: {reg['selected_model']}, selected by lowest test RMSE. Classification: {clf['selected_model']}, selected by highest test F1. KMeans: K={cluster['selected_k']}, maximum training silhouette. Comparison tables and actual errors appear in the report and JSONs. Test selection is permitted by the assignment but needs a fresh external evaluation before deployment. Probability calibration and prediction intervals are not established.

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
- tests/: meaningful integration and failure-path tests. Actual latest summary: **{test_summary}**.
- docs/AI_A2_2527343_REPORT.pdf: seven-page technical report; PERSONAL_REVIEW.md: required personal interpretation worksheet.
- evidence/: actual command/API/reproducibility captures, PDF test log, unsigned declaration, AI disclosure and recording checklist.

Row IDs are zero-based CSV data-row positions before deduplication. CSV regression error = predicted minus actual; plot residual = actual minus predicted. Cluster profiles describe training farms; observed means omit missing measurements. All K scores and confusion matrices are in JSON. Extra tools: httpx supports TestClient; reportlab generates PDFs; pypdf and PyMuPDF verify PDF page count and rendering. pytest is for automated checks; uvicorn serves the API.

## Submission status and repository

**PROVISIONAL**: authentic continuous unedited <=2-minute video, signature, and personally rewritten error/cluster interpretations are pending. Review AI_USE.md and the declaration for truthfulness. No personal reflection or video is claimed complete. Deadline: 19 October 2026, 5:00 PM CAT; Moodle timestamp is authoritative.

Repository URL: https://github.com/Sauverain/AI_A2_2527343

Obtain the current commit using `git log -1 --format=%H`; the package's evidence/FINAL_COMMIT.txt records the packaged implementation commit. After personal edits, commit again and use the final hash for the video.

```powershell
git remote add origin https://github.com/Sauverain/AI_A2_2527343.git
git push -u origin HEAD
```

Create the repository in your own account first; replace the placeholder with its actual URL. No remote was invented or pushed. Complete personal evidence, regenerate documentation as appropriate, run verification, commit changes, record the authentic video using that hash, rebuild and inspect the ZIP, then upload AI_A2_2527343.zip to INES e-learning before the deadline.

## Understanding and defense

The seed fixes the random sequence, and SHA-256 checks CSV bytes. Deduplication prevents identical copies crossing the split. Training-only medians/scaling prevent test distribution from influencing fitted transformations. Pipelines make saved inference match training. The mean and majority baselines show whether learning helps. RMSE penalizes large harvest errors; F1 balances precision/recall, while a missed risky farm may warrant special review. Silhouette compares feature cohesion and separation; a cluster is not a risk label. Read PERSONAL_REVIEW.md and explain one actual error and cluster in your own words. To change a field bound, update the shared schema and dataset bounds together and test valid/invalid boundary records.
'''
    (ROOT/'README.md').write_text(readme,encoding='utf-8')
    rubric = [['Category','Marks','Evidence / outstanding'],['Identity and reproducibility',8,'Confirmed name/email; config.py, fingerprint and two-run equality.'],['Data generation and validation',12,'generate_data.py, data_quality.json and validation tests.'],['Preprocessing and leakage',10,'Independent pipelines; stored medians tested against train rows.'],['Regression',12,'Three candidates, metrics, residuals; student error wording pending.'],['Classification',15,'Three candidates, metrics, probabilities and confusion matrices; personal error wording pending.'],['Clustering',10,'K=2..6, silhouette, profiles, labeled PCA; personal interpretation pending.'],['CLI and FastAPI',10,'Saved models, shared schema, actual TestClient and CLI evidence.'],['Testing and code quality',8,'Modular sources; actual pytest and reproducibility captures.'],['Report and responsible AI',10,'Seven-page report, model card and AI disclosure; student reflection pending.'],['Submission evidence and defense',5,'ZIP, Git hash, test log and checklist; video/signature/student defense pending.']]
    pdf(ROOT/'docs/RUBRIC_AUDIT.pdf',[Paragraph('Rubric evidence audit - not a grade',S['Heading1']),p('All ten categories total 100 marks. This maps evidence to requirements; it does not award marks or certify student authorship.'),table(rubric,[137,42,332])])
    print('Generated report, test log, unsigned declaration, README, disclosure and rubric audit.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-only', action='store_true', help='Update only the technical report; preserve all other documents.')
    main(report_only=parser.parse_args().report_only)

# Submission review — 19 October 2026

The supplied eight-page assignment was compared with the existing project. The technical implementation is present: registration-specific data generation, validation and cleaning, train-only preprocessing, regression and classification baselines plus two candidates each, K=2–6 clustering, saved pipelines, CLI, FastAPI, automated tests, plots and a seven-page report.

The report audit passed: metric tables agree with JSON, the dataset fingerprint agrees, and text remains within page boundaries. Current command results are saved in evidence/execution_log.json; two-run comparisons are in evidence/reproducibility.json and API responses in evidence/api_checks.json. These are executed checks, not a predicted grade.

## Required personal work before submission

1. Confirm that Alain Sauverain ISHEMA, registration 25/27343 and ug2527343@ines.ac.rw are your details. They were already configured in this project; this review did not independently verify identity.
2. Complete docs/PERSONAL_REVIEW.md in your own words: one actual regression error, one actual classification error, one cluster interpretation and your reflection. Incorporate your reviewed wording into the report source in tools/build_docs.py, replacing the pending-review statements. The PDF expressly requires your own interpretations.
3. Review evidence/AI_USE.md and the declaration for accuracy; amend them as needed and sign the declaration yourself.
4. Add your actual repository URL to README.md. Commit the reviewed source and record the resulting hash in the README or an explicitly referenced evidence file. No remote is currently configured. Keep the hash shown in your video consistent with the reviewed implementation.
5. Record evidence/AI_A2_2527343_DEMO.mp4 yourself: continuous, unedited, at most two minutes, with your voice, handwritten identity card, commit hash, clock and the demonstrations listed in evidence/DEMO_CHECKLIST.md. No video is currently present.
6. Rebuild the ZIP after adding your final evidence, inspect it, and upload it through INES e-learning. The PDF specifies 19 October 2026 at 17:00 CAT; Moodle's timestamp governs submission.

## Rebuilding safely

Run commands from the project folder using the activated environment. tools/build_docs.py overwrites the personal worksheet, declaration, AI disclosure, README and demo checklist. Preserve your personal edits before running it; update its source with reviewed wording or merge your edits afterward. Once personal evidence is complete, update the provisional status and pending list in tools/package.py to reflect the actual files and review state, then run python tools/package.py. Its current provisional status is intentional because the personal requirements remain outstanding.

The ZIP is technically verified but is not yet a complete submission. Personal authorship statements, a signature and an authentic demonstration cannot be supplied by an automated technical review.

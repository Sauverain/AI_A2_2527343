# Authentic demo checklist — video NOT yet supplied

Create evidence/AI_A2_2527343_DEMO.mp4 yourself. One continuous unedited MP4, maximum two minutes, your own voice. Rehearse beforehand; do not fake command results or splice recording. Keep text readable. Run the service beforehand in another terminal if useful.

- 0–12 s: Show handwritten card: Alain Sauverain ISHEMA, 25/27343, AI-A2-7343. Identify yourself in your own voice. Show terminal clock (`Get-Date`) and `git rev-parse HEAD`.
- 12–40 s: Execute `python run_all.py --student-id ug2527343@ines.ac.rw --seed 7343`; show fingerprint, metrics and artifact list.
- 40–55 s: Open one metric JSON and its plot; explain one result in your own words without reading a prepared script.
- 55–75 s: Run valid and invalid predict.py commands; show actual output and error.
- 75–100 s: Show http://127.0.0.1:8000/docs, health and a valid predict response plus a validation error.
- 100–120 s: Run `pytest -q`; show report, reviewed/signed declaration and terminal clock.

Before recording: understand the code and results, complete PERSONAL_REVIEW.md, sign the truthful declaration, use the final reviewed Git commit, prepare all windows, and time a rehearsal. If actual runtime exceeds this outline, adjust pacing while retaining the PDF's required evidence. Never speed up or edit the final continuous recording. After adding evidence, commit reviewed changes, use the new commit in the video, rebuild the ZIP, and verify contents.

"""Execute checks and preserve actual stdout, stderr and deterministic evidence."""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, STUDENT_ID, SEED, CODE

def main():
    """Run real commands twice; fail verification on an unexpected exit code."""
    evidence = ROOT / 'evidence'
    evidence.mkdir(exist_ok=True)
    records = []
    def execute(args, expected=0):
        env = dict(os.environ, PYTHONIOENCODING='utf-8', MPLBACKEND='Agg')
        result = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True, text=True)
        records.append({'command': 'python ' + ' '.join(args), 'exit_code': result.returncode,
            'expected_exit_code': expected, 'stdout': result.stdout, 'stderr': result.stderr})
        print(records[-1]['command'], 'exit', result.returncode, flush=True)
        (evidence / 'execution_log.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
        if result.returncode != expected:
            raise RuntimeError(result.stdout + result.stderr)
    command = ['run_all.py', '--student-id', STUDENT_ID, '--seed', str(SEED)]
    execute(command)
    paths = ['artifacts/data_fingerprint.txt', 'artifacts/regression_metrics.json', 'artifacts/classification_metrics.json', 'artifacts/clustering_report.json', 'artifacts/test_predictions.csv']
    before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    execute(command)
    after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    same = before == after
    (evidence / 'reproducibility.json').write_text(json.dumps({'verification_code': CODE, 'utc_time': datetime.now(timezone.utc).isoformat(), 'exact_match': same, 'first_run_sha256': before, 'second_run_sha256': after}, indent=2), encoding='utf-8')
    if not same: raise RuntimeError('Reproducibility mismatch')
    execute(['predict.py', '--json', 'samples/valid.json'])
    execute(['predict.py', '--json', 'samples/invalid.json'], 2)
    execute(['run_all.py', '--student-id', STUDENT_ID, '--seed', '0'], 2)
    execute(['-m', 'pytest', '-q', '-ra'])
    from fastapi.testclient import TestClient
    from app import app
    valid = json.loads((ROOT / 'samples/valid.json').read_text())
    checks = []
    with TestClient(app) as client:
        for method, url, kwargs in [('GET', '/health', {}), ('GET', '/model-info', {}), ('GET', '/docs', {}), ('POST', '/predict', {'json': valid}), ('POST', '/predict', {'json': {}}), ('POST', '/predict', {'content': '{bad', 'headers': {'Content-Type': 'application/json'}})]:
            response = client.request(method, url, **kwargs)
            checks.append({'method': method, 'url': url, 'status': response.status_code, 'body': response.json() if url != '/docs' else 'Swagger HTML returned'})
    (evidence / 'api_checks.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
    print('Deterministic fingerprints and metrics:', same)

if __name__ == '__main__': main()

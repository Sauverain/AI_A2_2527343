"""Package only project deliverables and verify every stored file."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, CODE

def main():
    """Create a manifest, record the real Git hash and inspect ZIP structure."""
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (ROOT/'evidence/FINAL_COMMIT.txt').write_text(commit+'\n',encoding='utf-8')
    required = ['README.md','requirements.txt','run_all.py','predict.py','app.py','data/generate_data.py','data/AI_A2_2527343.csv','samples/valid.json','samples/invalid.json',
        'artifacts/data_fingerprint.txt','artifacts/regression_metrics.json','artifacts/classification_metrics.json','artifacts/clustering_report.json','artifacts/test_predictions.csv',
        'artifacts/plots/residuals.png','artifacts/plots/confusion_matrix.png','artifacts/plots/clusters.png','models/regression.joblib','models/classification.joblib','models/clustering.joblib',
        'docs/AI_A2_2527343_REPORT.pdf','evidence/AI_A2_2527343_TEST_LOG.pdf','evidence/AI_A2_2527343_DECLARATION.pdf','evidence/AI_USE.md']
    assert all((ROOT/p).is_file() for p in required), 'Required technical deliverable missing'
    excluded = {'.git','.venv','__pycache__','.pytest_cache'}
    files = [p for p in ROOT.rglob('*') if p.is_file() and not excluded.intersection(p.relative_to(ROOT).parts) and p.suffix not in {'.pyc','.zip'} and p.name not in {'PACKAGE_MANIFEST.json','.env'}]
    manifest = {'verification_code': CODE, 'commit': commit, 'status': 'PROVISIONAL',
        'pending': ['Student review and personal interpretations', 'Student signature', 'Authentic continuous unedited <=2-minute personal demonstration'],
        'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
    manifest_path = ROOT/'evidence/PACKAGE_MANIFEST.json'
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    files.append(manifest_path)
    target = ROOT.parent / (ROOT.name+'.zip')
    with ZipFile(target,'w',compression=ZIP_DEFLATED) as z:
        for p in sorted(files): z.write(p, (Path(ROOT.name)/p.relative_to(ROOT)).as_posix())
    with ZipFile(target) as z:
        assert z.testzip() is None
        assert all(n.startswith(ROOT.name+'/') for n in z.namelist())
        for path, digest in manifest['files'].items():
            assert hashlib.sha256(z.read(ROOT.name+'/'+path)).hexdigest() == digest
        assert all(ROOT.name+'/'+p in z.namelist() for p in required)
        print(f'ZIP verified: {len(z.namelist())} files, {target.stat().st_size} bytes; {target}; PROVISIONAL')
        print('Commit:',commit)

if __name__ == '__main__': main()

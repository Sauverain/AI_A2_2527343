"""Check report pagination, artifact agreement and forbidden signature values."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pymupdf as fitz
from pypdf import PdfReader
from src.config import ROOT, CODE

def main():
    """Render every report page, check text bounds and verify rounded metrics."""
    path = ROOT/'docs/AI_A2_2527343_REPORT.pdf'
    reader = PdfReader(path)
    assert len(reader.pages) == 7, f'Expected 7 pages, found {len(reader.pages)}'
    text = '\n'.join(p.extract_text() for p in reader.pages)
    assert CODE in text and 'Alain Sauverain ISHEMA' in text
    fp = (ROOT/'artifacts/data_fingerprint.txt').read_text().strip()
    assert fp in re.sub(r'\s','',text)
    for task in ['regression','classification']:
        evidence = json.loads((ROOT/f'artifacts/{task}_metrics.json').read_text())
        assert evidence['selected_model'] in text
        for m in evidence['candidates'].values():
            for key,value in m.items():
                if key != 'confusion_matrix' and value is not None:
                    assert f'{value:.4f}' in text, f'Missing metric {key}'
    cluster = json.loads((ROOT/'artifacts/clustering_report.json').read_text())
    for score in cluster['scores'].values(): assert f'{score:.5f}' in text
    render_dir = ROOT/'evidence/report_preview'
    render_dir.mkdir(exist_ok=True)
    doc = fitz.open(path)
    for i,page in enumerate(doc):
        for block in page.get_text('blocks'):
            assert block[0]>=25 and block[1]>=15 and block[2]<=page.rect.width-20 and block[3]<=page.rect.height-15, f'Text out of bounds on page {i+1}: {block}'
        page.get_pixmap(matrix=fitz.Matrix(1,1)).save(render_dir/f'page_{i+1}.png')
    # Compact montage supports visual review without replacing full-page inspection.
    from PIL import Image, ImageOps, ImageDraw
    montage = Image.new('RGB',(900,1280),'#d8e0e4')
    for i in range(7):
        im = Image.open(render_dir/f'page_{i+1}.png').convert('RGB')
        im.thumbnail((290,405))
        montage.paste(im,((i%3)*300,(i//3)*425))
    montage.save(render_dir/'montage.png')
    failures=[]
    for file in ROOT.rglob('*'):
        if not file.is_file() or any(part in {'.venv','.git','__pycache__','.pytest_cache'} for part in file.relative_to(ROOT).parts): continue
        if file.suffix not in {'.py','.md','.txt','.json','.csv','.pdf'}: continue
        contents = '\n'.join(p.extract_text() for p in PdfReader(file).pages) if file.suffix=='.pdf' else file.read_text(encoding='utf-8')
        # Construct forbidden signatures so the audit itself does not contain them.
        forbidden = ['25/'+str(27340+1), 'AI-A2-'+str(7340+1)]
        if any(v in contents for v in forbidden) or re.search(r'(?<![\w.])'+str(7340+1)+r'(?![\w.])',contents): failures.append(str(file))
    assert not failures, failures
    report={'verification_code': CODE,'report_pages':7,'metric_tables_match_json':True,'fingerprint_matches':True,'text_within_page_bounds':True,'forbidden_identity_values_found':False,'rendered_pages':7,'rubric_categories':10,'rubric_marks_total':100}
    (ROOT/'evidence/document_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()

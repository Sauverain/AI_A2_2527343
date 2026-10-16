"""Generate the exact registration-specific CSV without manual editing."""
import hashlib
import sys
from pathlib import Path
import numpy
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, SEED

def generate_data(output=None):
    """Write CSV and hash its final bytes; return raw rows and SHA-256."""
    rng = numpy.random.default_rng(7343)
    n = 240 + (SEED % 41)
    frame = pd.DataFrame({
        'rainfall_mm': rng.uniform(600, 1400, n),
        'avg_temp_c': rng.uniform(12, 26, n),
        'soil_moisture_pct': rng.uniform(20, 80, n),
        'fertilizer_kg': rng.uniform(0, 250, n),
        'field_size_ha': rng.uniform(0.2, 4, n),
        'season': rng.choice(['A', 'B'], n),
        'cooperative_support': rng.choice([0, 1], n),
    })
    frame['yield_tons'] = numpy.maximum(0.50,
        .004 * frame.rainfall_mm + .06 * frame.soil_moisture_pct
        + .02 * frame.fertilizer_kg + 1.30 * frame.field_size_ha
        - .25 * abs(frame.avg_temp_c - 18) + .70 * frame.cooperative_support
        + numpy.where(frame.season == 'A', .50, -.20) + rng.normal(0, .80, n))
    per_ha = frame.yield_tons / frame.field_size_ha
    frame['high_risk'] = (per_ha < per_ha.median()).astype(int)
    m = round(.05 * n)
    for column in ['soil_moisture_pct', 'fertilizer_kg']:
        frame.loc[rng.choice(n, m, replace=False), column] = numpy.nan
    # First three rows are the documented exact duplicate source records.
    frame = pd.concat([frame, frame.iloc[:3]], ignore_index=True)
    output = Path(output) if output else ROOT / 'data/AI_A2_2527343.csv'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(frame.to_csv(index=False, float_format='%.4f', lineterminator='\n'), encoding='utf-8', newline='')
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    if output == ROOT / 'data/AI_A2_2527343.csv':
        (ROOT / 'artifacts').mkdir(exist_ok=True)
        (ROOT / 'artifacts/data_fingerprint.txt').write_text(digest + '\n', encoding='utf-8')
    return pd.read_csv(output), digest

if __name__ == '__main__':
    rows, fingerprint = generate_data()
    print(f'{len(rows)} rows; SHA-256 {fingerprint}')

"""Identity, paths and feature contract."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 7343
STUDENT_ID = 'ug2527343@ines.ac.rw'
NAME = 'Alain Sauverain ISHEMA'
CODE = 'AI-A2-7343'
NUMERIC = ['rainfall_mm', 'avg_temp_c', 'soil_moisture_pct', 'fertilizer_kg', 'field_size_ha', 'cooperative_support']
FEATURES = NUMERIC + ['season']
TARGETS = ['yield_tons', 'high_risk']
BOUNDS = {'rainfall_mm': (600, 1400), 'avg_temp_c': (12, 26), 'soil_moisture_pct': (20, 80), 'fertilizer_kg': (0, 250), 'field_size_ha': (0.2, 4), 'cooperative_support': (0, 1)}

def validate_identity(student_id, seed):
    """Reject a signature other than this student's assigned identity."""
    if student_id != STUDENT_ID or seed != SEED:
        raise ValueError(f'Expected --student-id {STUDENT_ID} --seed {SEED}; incorrect identity or seed.')

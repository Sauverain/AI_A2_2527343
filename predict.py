"""Predict from one JSON record using saved models, without retraining."""
import argparse
import json
from pathlib import Path
from pydantic import ValidationError
from src.validation import FarmRecord
from src.inference import Predictor

def main():
    """Validate input with the same schema as FastAPI; return useful exit codes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', required=True, type=Path)
    args = parser.parse_args()
    try:
        record = FarmRecord.model_validate_json(args.json.read_text(encoding='utf-8'))
        print(json.dumps(Predictor().predict(record), indent=2, allow_nan=False))
    except (ValidationError, ValueError, OSError) as exc:
        parser.exit(2, f'Input/model error: {exc}\n')

if __name__ == '__main__':
    main()

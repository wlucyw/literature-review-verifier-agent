from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.schemas import TrainingSample


SYSTEM_PROMPT = """You are a literature verification model.
Rules:
1. Never fabricate citation metadata.
2. Ground every judgement in retrieval evidence and rule results.
3. If evidence is insufficient, output uncertain.
4. Return strict JSON only.
"""



def format_training_sample(sample: TrainingSample) -> Dict[str, str]:
    prompt = (
        f"<system>\n{SYSTEM_PROMPT}\n</system>\n"
        f"<instruction>\n{sample.instruction}\n</instruction>\n"
        f"<input>\n{json.dumps(sample.input, ensure_ascii=False)}\n</input>\n"
        "<output_json>"
    )
    completion = json.dumps(sample.output, ensure_ascii=False)
    return {"prompt": prompt, "completion": completion, "text": prompt + completion}

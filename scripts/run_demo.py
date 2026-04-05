from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.schemas import VerifyRequest
from app.services.verify_service import VerifyService


if __name__ == "__main__":
    sample = json.loads((ROOT_DIR / "data" / "samples" / "sample_input.json").read_text(encoding="utf-8-sig"))
    response = VerifyService().verify(VerifyRequest(**sample))
    print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))

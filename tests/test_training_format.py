import json
from pathlib import Path

from app.core.schemas import TrainingSample
from training.formatters import format_training_sample



def test_training_formatter_outputs_prompt() -> None:
    line = Path("data/samples/toy_train.jsonl").read_text(encoding="utf-8-sig").splitlines()[0]
    sample = TrainingSample.model_validate(json.loads(line))
    formatted = format_training_sample(sample)
    assert "<system>" in formatted["prompt"]
    assert formatted["completion"].startswith("{")

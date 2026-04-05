from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sklearn.metrics import accuracy_score

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.llm.dummy_llm import DummyLLMClient
from training.build_dataset import load_samples
from training.formatters import format_training_sample


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--val_file", required=True)
    args = parser.parse_args()

    samples = load_samples(Path(args.val_file))
    client = DummyLLMClient()
    y_true = [sample.output.get("support_label", "uncertain") for sample in samples]
    y_pred = []
    exact = 0
    for sample in samples:
        formatted = format_training_sample(sample)
        pred = json.loads(client.generate_json(formatted["prompt"]))
        y_pred.append(pred.get("support_label", "uncertain"))
        if pred == sample.output:
            exact += 1

    print(json.dumps({"samples": len(samples), "label_accuracy": accuracy_score(y_true, y_pred) if samples else 0.0, "exact_match_ratio": exact / len(samples) if samples else 0.0}, ensure_ascii=False, indent=2))

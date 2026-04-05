from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.schemas import TrainingSample
from training.formatters import format_training_sample



def load_samples(path: Path) -> List[TrainingSample]:
    samples = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        samples.append(TrainingSample.model_validate(json.loads(line)))
    return samples



def split_samples(samples: List[TrainingSample], val_ratio: float, seed: int = 42) -> Tuple[List[TrainingSample], List[TrainingSample]]:
    rng = random.Random(seed)
    shuffled = samples[:]
    rng.shuffle(shuffled)
    val_size = max(1, int(len(shuffled) * val_ratio)) if len(shuffled) > 1 else 0
    return shuffled[val_size:], shuffled[:val_size]



def save_jsonl(items, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--val_ratio", type=float, default=0.2)
    args = parser.parse_args()

    samples = load_samples(Path(args.input_file))
    train_samples, val_samples = split_samples(samples, args.val_ratio)
    save_jsonl([sample.model_dump() for sample in train_samples], Path(args.output_dir) / "train.jsonl")
    save_jsonl([sample.model_dump() for sample in val_samples], Path(args.output_dir) / "val.jsonl")
    save_jsonl([format_training_sample(sample) for sample in train_samples], Path(args.output_dir) / "train_formatted.jsonl")
    save_jsonl([format_training_sample(sample) for sample in val_samples], Path(args.output_dir) / "val_formatted.jsonl")

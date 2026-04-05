from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from training.formatters import SYSTEM_PROMPT


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", required=True)
    parser.add_argument("--adapter_path", required=True)
    parser.add_argument("--instruction", required=True)
    parser.add_argument("--input_json", required=True)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path, trust_remote_code=True)
    model = PeftModel.from_pretrained(model, args.adapter_path)

    prompt = (
        f"<system>\n{SYSTEM_PROMPT}\n</system>\n"
        f"<instruction>\n{args.instruction}\n</instruction>\n"
        f"<input>\n{args.input_json}\n</input>\n"
        "<output_json>"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=args.max_new_tokens)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))

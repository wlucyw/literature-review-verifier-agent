from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments

from training.build_dataset import load_samples
from training.formatters import format_training_sample


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", required=True)
    parser.add_argument("--train_file", required=True)
    parser.add_argument("--val_file", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--max_length", type=int, default=1024)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--num_train_epochs", type=float, default=1.0)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--lora_r", type=int, default=8)
    parser.add_argument("--lora_alpha", type=int, default=16)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path, trust_remote_code=True)
    peft_config = LoraConfig(task_type=TaskType.CAUSAL_LM, r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=args.lora_dropout, target_modules=["q_proj", "v_proj"])
    model = get_peft_model(model, peft_config)

    def to_dataset(path_str: str) -> Dataset:
        records = [format_training_sample(sample) for sample in load_samples(Path(path_str))]
        ds = Dataset.from_list(records)
        return ds.map(lambda batch: tokenizer(batch["text"], truncation=True, max_length=args.max_length), batched=True, remove_columns=ds.column_names)

    train_dataset = to_dataset(args.train_file)
    val_dataset = to_dataset(args.val_file)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_train_epochs,
        logging_steps=5,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        report_to="none",
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )
    trainer.train()
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

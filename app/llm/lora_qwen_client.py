from __future__ import annotations

import json

from app.core.config import get_settings
from app.llm.base_llm import BaseLLMClient


class LoRAQwenClient(BaseLLMClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        self._pipeline = None

    def _load(self) -> None:
        if self._pipeline is not None:
            return
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        if not self.settings.lora_adapter_path:
            raise ValueError("LORA_ADAPTER_PATH is not configured.")
        tokenizer = AutoTokenizer.from_pretrained(self.settings.hf_model_name_or_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            self.settings.hf_model_name_or_path,
            device_map=self.settings.device_map,
            trust_remote_code=True,
        )
        model = PeftModel.from_pretrained(model, self.settings.lora_adapter_path)
        self._pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

    def generate_json(self, prompt: str) -> str:
        self._load()
        outputs = self._pipeline(prompt, max_new_tokens=256, do_sample=False)
        text = outputs[0]["generated_text"][len(prompt) :].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Model did not return JSON")
        json.loads(text[start : end + 1])
        return text[start : end + 1]

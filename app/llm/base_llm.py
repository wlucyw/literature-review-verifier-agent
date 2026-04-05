from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> str:
        raise NotImplementedError

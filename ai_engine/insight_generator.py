import os
import ollama


class InsightGenerator:
    """Generates natural language insights from data results using Ollama."""

    def __init__(self, model: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")

    def generate(self, prompt: str) -> str:
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0.4, "num_predict": 700},
        )
        return response["response"].strip()

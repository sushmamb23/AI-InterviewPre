import os
import ollama

OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

DEFAULT_MODELS = [
    os.getenv("OLLAMA_MODEL", "").strip(),
    "llama3.2:latest",
    "qwen3:8b",
    "llama3.2:3b",
]


def resolve_model() -> str:
    candidates = []
    seen = set()
    for model in DEFAULT_MODELS:
        if model and model not in seen:
            candidates.append(model)
            seen.add(model)

    try:
        available = ollama.list()
        available_names = {model.get("name") for model in available.get("models", []) if model.get("name")}
        for model in candidates:
            if model in available_names:
                return model
    except Exception:
        pass

    return candidates[0] if candidates else "llama3.2:latest"


def chat(prompt: str) -> str:
    try:
        model = resolve_model()
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 300},
            keep_alive="5m",
        )
        return response["message"]["content"]
    except Exception as exc:
        return f"Ollama unavailable: {exc}"

# AI Interview Coach

This project provides a LangGraph-based interview coaching workflow that analyzes a candidate resume, identifies gaps, generates interview questions, and produces a report.

## Quick start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
3. Start the frontend:
   ```bash
   streamlit run frontend.py
   ```

## Docker

```bash
docker compose up --build
```

## Notes

- The app uses Ollama for LLM-based content generation. Make sure Ollama is running and the model is available.
- If Ollama is unavailable, the app falls back to deterministic mock guidance.

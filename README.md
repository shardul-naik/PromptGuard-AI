# PromptGuard-AI

PromptGuard-AI is a FastAPI backend with a Streamlit frontend for prompt security scanning, semantic caching, model routing, and response generation.

## Setup

1. Create or activate the project environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   python -m pip install -r backend\requirements.txt
   ```

3. Create `.env` in the project root and set `OPENAI_API_KEY`.

## Run

Start the backend from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

In a second terminal, start the frontend:

```powershell
streamlit run frontend\app.py
```

The API is available at `http://127.0.0.1:8000`; the health check is `/health`.
# Analyzer Pro Web

A separate browser-based interface for Analyzer Pro. The original PySide6 desktop app remains untouched.

## Run locally

Use Python 3.11 or newer in a fresh virtual environment. From the repository root:

```powershell
py -3.12 -m venv .venv-web
.\.venv-web\Scripts\Activate.ps1
python -m pip install -r requirements-web.txt
python -m streamlit run web/app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

## Deploy to Streamlit Community Cloud

1. Create a new app in Streamlit Community Cloud.
2. Select repository `woriachrizz/AnalyzerPro`.
3. Select branch `web-app`.
4. Set main file path to `web/app.py`.
5. Deploy. Dependencies are in `requirements-web.txt`.

The app uses Deriv's public market-data WebSocket endpoint for read-only ticks. No Deriv account token is required or stored. Never add account tokens, passwords, or credentials to this repository.

Each browser session has its own analyzer and WebSocket connection. Changing markets resets that session's collected statistics. Model estimates are descriptive analytics, not guarantees or trading advice.

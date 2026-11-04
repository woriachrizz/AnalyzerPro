# Analyzer Pro Web

A browser-based companion to the existing PySide6 desktop application. The desktop UI and desktop entry point are not modified.

## Run locally

From the repository root:

```powershell
python -m pip install -r web/requirements.txt
python -m streamlit run web/app.py
```

Open the localhost URL printed by Streamlit (normally http://localhost:8501).

## Deploy on Streamlit Community Cloud

1. Push the `web-version` branch to GitHub.
2. Sign in at https://share.streamlit.io/ using GitHub.
3. Create an app for repository `woriachrizz/AnalyzerPro`.
4. Select branch `web-version`.
5. Set the main file path to `web/app.py`.
6. Deploy. The dependency file is `web/requirements.txt`.

## Notes

- Uses the same public Deriv WebSocket endpoint as the desktop client.
- No Deriv account token is requested for public market data.
- Each browser session has its own in-memory analysis state.
- Tick history is not persisted after the browser session ends.
- Statistical estimates are not guarantees or trading instructions.

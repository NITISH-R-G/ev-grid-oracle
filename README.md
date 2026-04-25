---
title: EV Grid Oracle (OpenEnv)
emoji: ⚡
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

## EV Grid Oracle — OpenEnv Environment

This Space hosts the **OpenEnv-compatible FastAPI server** for `EVGridEnvironment`.

### Endpoints

- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /schema`
- `GET /health`

### Local dev

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Demo UI

The Gradio demo is in `viz/gradio_demo.py` (separate Space recommended).


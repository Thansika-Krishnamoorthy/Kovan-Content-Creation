# Kovan Content Creation

This repository has two workflows:

- `prompt-generation` is the offline prompt studio. It generates a copy/paste-ready prompt and shows the approved logo plus optional speaker photo for use in any image generator.
- `openrouter-seedream` adds a FastAPI proxy and an in-page Seedream 4.5 generation workflow. The OpenRouter key stays on the server, and the selected official logo is composited unchanged into the downloaded PNG.

## Seedream workflow

Create a virtual environment, install dependencies, and set the server key:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key
.venv/bin/uvicorn server:app --reload
```

Open <http://127.0.0.1:8000>. Image generation uses paid OpenRouter requests; do not put the API key in the HTML or commit `.env` files.

# ReasonDiff

Visualize where LLM reasoning chains diverge between different models or prompts.

## Why it matters

ReasonDiff answers a critical question in production LLM systems: **Where exactly did the reasoning chains differ?** This pairs perfectly with [SilentRegression](https://github.com/trinathone/silent-regression), which detects *when* reasoning drifts — ReasonDiff shows *why* and *where*.

Use cases:
- MLOps engineers debugging model behavior across NVIDIA NIM instances
- Prompt engineers comparing system prompt variations
- AI platform teams detecting reasoning quality regressions
- Developers investigating why deepseek-r1 and llama-3.3 solve the same problem differently

## Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Set up API keys
ReasonDiff reads NVIDIA NIM API keys from `~/keys/api_keys.py`. The expected format:
```python
# ~/keys/api_keys.py
NVIDIA_MODELS = {
    'nemotron': 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
    'deepseek': 'deepseek-ai/deepseek-r1',
    'qwq': 'qwen/qwq-32b',
    'llama': 'meta/llama-3.3-70b-instruct',
}

class nvidia_chat:
    api_key = "your-nvidia-nim-api-key"
```

If `api_keys.py` is missing or API key is not set, the tool runs in mock mode and generates placeholder responses (useful for UI testing).

### Run the server
```bash
uvicorn main:app --port 8007
```

Open http://localhost:8007 in your browser.

## How it works

1. **Configure both models** — select Model A and Model B from NVIDIA NIM
2. **Enter prompts** — system prompt + user prompt (same for both models)
3. **Run diff** — tool calls both models in parallel and extracts reasoning chains
4. **View results** — side-by-side colored diff shows exactly where reasoning diverged

### Reasoning extraction
ReasonDiff handles multiple response formats:
- **DeepSeek R1**: reads `response.choices[0].message.reasoning_content`
- **Nemotron/QwQ**: extracts `<think>...</think>` blocks from content
- **Fallback**: parses `<reasoning>` tags or returns full content

### Diff algorithm
- Splits reasoning into sentences (on `. ` and `\n`)
- Uses Python's `difflib.SequenceMatcher` for optimal alignment
- Color-codes output: 
  - 🟢 Green = added (Model B only)
  - 🔴 Red = removed (Model A only)  
  - 🟡 Yellow = changed

### Stats
- **Similarity score** — 0-100% overlap in reasoning
- **Divergence point** — which sentence first differed
- **Reasoning length** — char count for both models

## File structure
```
~/repos/reasondiff/
├── main.py              # FastAPI app + endpoints
├── diff_engine.py       # reasoning extraction + diff logic
├── llm_client.py        # NVIDIA NIM API client
├── static/
│   └── index.html       # Single-page UI (dark theme)
├── requirements.txt
├── README.md
└── CLAUDE.md           # Build spec
```

## API Endpoints

- `GET /` — serve UI
- `POST /diff` — compute diff
  - Body: `{model_a, model_b, system_prompt, user_prompt}`
  - Returns: reasoning chains, similarity score, colored diff HTML
- `GET /health` — health check
- `GET /models` — available NVIDIA NIM models

## Features

### Core MVP ✅
- Two-panel input for model A and model B configs
- Live API calls to NVIDIA NIM
- Reasoning content extraction (multiple formats)
- Side-by-side colored diff view
- Similarity score & divergence point detection
- Final answer comparison

### Nice to have
- Save snapshots to `/tmp/reasondiff_snapshots/`
- Batch mode for 3+ models
- Search within diffs
- Keyboard shortcuts

## No API key? No problem

Running without `~/keys/api_keys.py` or without a valid API key? The UI still works perfectly. The tool generates mock reasoning chains so you can test the UI and diff algorithm locally.

## Stack
- **Backend**: FastAPI (Python 3.11) + uvicorn
- **Frontend**: Vanilla JS, no framework
- **Diff algorithm**: Python `difflib`
- **LLM API**: NVIDIA NIM (async via httpx)
- **Styling**: Dark theme (GitHub-inspired #0d1117 palette)

## Related tools
- [SilentRegression](https://github.com/trinathone/silent-regression) — detects when reasoning drifts
- LiteLLM #25 — "DeepSeek V4 Pro strips reasoning_content"
- MLflow #19 — "No histogram plot logging over time"

## License
MIT

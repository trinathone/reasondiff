# ReasonDiff — Build Spec

## What it is
A lightweight web tool that diffs LLM reasoning chains between two runs — different models, different prompts, or different versions of the same prompt. Shows WHERE reasoning diverged, not just what the final answer was.

## Why it exists (real pain)
1. LiteLLM #25 most-voted open issue: "DeepSeek V4 Pro strips reasoning_content from assistant messages in multi-turn" — people are losing reasoning traces and can't debug it
2. MLflow #19 most-voted: "No histogram plot logging over time" — no way to see reasoning quality drift over time
3. SilentRegression (Trinath's own tool, port 8005) detects WHEN reasoning drifts — ReasonDiff shows WHY and WHERE exactly
4. "Show HN: I built a web tool to see and edit what an AI thinks before it answers" got 34pts today — appetite is real

## Who pays
MLOps engineers, AI platform teams, prompt engineers at companies running multiple LLM versions in parallel. Direct companion to SilentRegression.

## Stack
- FastAPI backend (Python 3.11)
- Single-page HTML frontend (no framework, pure JS)
- Port: 8007
- difflib (stdlib) for text diff
- NVIDIA NIM API for live reasoning (use keys from ~/keys/api_keys.py)
- No DB — stateless, results computed on demand

## Features to build

### Core (MVP)
1. **Two-panel input** — left: Model A config (model name, system prompt, user prompt), right: Model B config
2. **Run both** — hits NVIDIA NIM for both, extracts reasoning_content (thinking tokens) from response
3. **Reasoning diff view** — side-by-side colored diff of the two reasoning chains (green=added, red=removed, yellow=changed)
4. **Summary stats** — similarity score (0-100%), divergence point (which sentence), reasoning length comparison
5. **Final answer comparison** — simple before/after of the final output

### Nice to have (build if time)
6. **Save snapshot** — store the diff as JSON to /tmp/reasondiff_snapshots/
7. **Batch mode** — run same prompt against 3+ models at once

## API Endpoints
- `GET /` → serve the HTML UI
- `POST /diff` → body: `{model_a, model_b, system_prompt, user_prompt}` → returns diff JSON
- `GET /health` → `{"status": "ok", "service": "reasondiff"}`
- `GET /models` → returns list of available NVIDIA NIM models

## File structure
```
~/repos/reasondiff/
├── main.py          # FastAPI app
├── diff_engine.py   # reasoning extraction + diff logic
├── llm_client.py    # NVIDIA NIM client (reuse ~/keys/api_keys.py pattern)
├── static/
│   └── index.html   # Single page UI
├── requirements.txt
└── README.md
```

## NVIDIA NIM models to support
From ~/keys/api_keys.py:
- nvidia/llama-3.1-nemotron-ultra-253b-v1 (best reasoning)
- deepseek-ai/deepseek-r1 (has reasoning_content)
- qwen/qwq-32b (reasoning model)
- meta/llama-3.3-70b-instruct (baseline comparison)

Import pattern:
```python
import sys
sys.path.insert(0, '/Users/tnt/keys')
from api_keys import nvidia_chat, NVIDIA_MODELS
```

## Reasoning content extraction
Models return reasoning in different fields:
- DeepSeek R1: response.choices[0].message.reasoning_content
- Nemotron/QwQ: sometimes in <think>...</think> tags inside content
- Fallback: extract <think>...</think> or <reasoning>...</reasoning> from content string

Build a robust extractor that handles all three patterns.

## Diff algorithm
Use Python's difflib.SequenceMatcher on sentence-split reasoning text:
1. Split reasoning into sentences (split on ". " or "\n")
2. Run SequenceMatcher
3. Return opcodes with matched/inserted/deleted/replaced segments
4. Frontend renders with color coding

## UI Design
- Dark theme (#0d1117 background like GitHub dark)
- Two columns: Model A (left, blue accent) | Model B (right, purple accent)
- Bottom: diff view with red/green highlights
- Stats bar: similarity %, reasoning tokens, divergence point
- Run button triggers both API calls in parallel (Promise.all)
- No login, no auth, just works

## README.md
Must include:
- What it does (1 sentence)
- Why it matters (the SilentRegression connection)
- Quick start: `pip install -r requirements.txt && uvicorn main:app --port 8007`
- Screenshot placeholder
- Link to SilentRegression: https://github.com/trinathone/silent-regression

## Requirements.txt
```
fastapi
uvicorn
difflib  # stdlib, no install needed
httpx
python-dotenv
```

## After building
1. Run `python3 -m py_compile main.py diff_engine.py llm_client.py` — must pass
2. Check `uvicorn main:app --port 8007 --help` works
3. Do NOT start the server
4. Create README.md with proper description
5. Output a summary of what was built

## Rules
- Do NOT start the server
- Do NOT make any API calls to NVIDIA during build
- Do NOT import api_keys at module level — only inside functions (avoids errors if key file missing)
- Use ONLY port 8007 — don't conflict with 8001-8006
- Keep it simple — this is a 1-day build, not an enterprise platform

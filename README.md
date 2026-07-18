# ReasonDiff

**Ever wondered why two AI models give you different answers to the exact same question?**

ReasonDiff shows you exactly where their thinking split — sentence by sentence.

---

## The Problem It Solves

You ask GPT-4 and DeepSeek the same question. You get different answers. But *why*? At what point did they start thinking differently? Was it the first sentence of reasoning, or did they agree for 80% of the way and then diverge at the end?

Right now there's no easy way to see this. You just get two answers and have to read both and figure it out yourself.

ReasonDiff does it automatically — runs both models, extracts their internal reasoning (the "thinking" part), and gives you a colored diff like a Git diff for thoughts.

---

## Real Use Cases

### "I upgraded my AI model — why is it behaving differently?"
You were using DeepSeek R1 and switched to Nemotron. Some answers changed. You want to know *where the logic diverged* — not just that it did.

Run both models on the same prompt. ReasonDiff shows you the exact sentence where reasoning split. You find out: the old model assumed the user wanted a short answer, the new model assumed they wanted detail. One sentence difference, totally different output.

### "My AI coding assistant gives wrong answers on edge cases"
You're comparing two prompt versions — one system prompt vs another. The outputs look similar but one occasionally fails. ReasonDiff shows you both reasoning chains side by side. The failing version skips a safety check the working one does every time. Found it in 30 seconds.

### "Which model is actually thinking harder about my problem?"
You're picking between 3 models for a production use case. Don't just compare final answers — compare the reasoning depth. ReasonDiff shows you reasoning length, similarity score, and where each model's logic is stronger.

### "My AI gave the wrong answer — where did it go wrong?"
Paste the same prompt into two model configs: the model that got it right vs the one that got it wrong. See exactly where the reasoning diverged. Now you know whether to fix the prompt, switch models, or both.

---

## How It Works

1. Pick two models (or two prompt versions for the same model)
2. Enter your prompt
3. Hit Run — both models respond in parallel
4. See a side-by-side colored diff of their reasoning chains

Color coding:
- 🟢 Green = this model added this reasoning the other didn't
- 🔴 Red = this model skipped something the other included
- 🟡 Yellow = same idea, said differently

Stats you get: similarity score (0-100%), which sentence first diverged, reasoning length for each model.

---

## Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --port 8007
```

Open http://localhost:8007

No API key? It runs in demo mode with mock responses so you can explore the UI first.

---

## Supported Models (via NVIDIA NIM)

- DeepSeek R1 — reasoning model, exposes full `reasoning_content`
- Nemotron 253B — NVIDIA's flagship, extracts `<think>` blocks
- QwQ 32B — Qwen reasoning model
- Llama 3.3 70B — solid baseline for comparison

---

## API

```
POST /diff
{
  "model_a": "deepseek-ai/deepseek-r1",
  "model_b": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
  "system_prompt": "You are a helpful assistant.",
  "user_prompt": "Should I use Redis or Postgres for storing user sessions?"
}
```

Returns: reasoning chains, similarity score, divergence point, colored HTML diff.

---

## Stack

- FastAPI + Python 3.11
- Vanilla JS frontend, no framework
- `difflib` for sentence-level diff
- NVIDIA NIM for model inference
- Dark theme UI

---

## Related

- [SilentRegression](https://github.com/trinathone/silent-regression) — detects *when* model reasoning starts drifting in production. ReasonDiff shows *where* and *why*.

---

## License

MIT

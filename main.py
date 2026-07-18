import asyncio
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from diff_engine import extract_reasoning, diff_reasoning_chains
from llm_client import NIMClient

app = FastAPI(title="ReasonDiff", version="0.1.0")
nim_client = NIMClient()

# Serve static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


class DiffRequest(BaseModel):
    model_a: str
    model_b: str
    system_prompt: str
    user_prompt: str


class DiffResponse(BaseModel):
    model_a: str
    model_b: str
    reasoning_a: str
    reasoning_b: str
    final_answer_a: str
    final_answer_b: str
    similarity_score: float
    divergence_point: Optional[int]
    reasoning_a_length: int
    reasoning_b_length: int
    sentences_a_count: int
    sentences_b_count: int
    left_diff_html: str
    right_diff_html: str


@app.get("/")
async def serve_ui() -> FileResponse:
    """Serve the main UI."""
    ui_path = static_path / "index.html"
    if ui_path.exists():
        return FileResponse(ui_path)
    return FileResponse(str(ui_path), media_type="text/html")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "reasondiff"}


@app.get("/models")
async def get_models() -> dict:
    """Return available models."""
    return {"models": nim_client.get_available_models()}


@app.post("/diff")
async def compute_diff(request: DiffRequest) -> DiffResponse:
    """Compute reasoning diff between two models."""
    try:
        # Call both models in parallel
        response_a, response_b = await asyncio.gather(
            nim_client.call_model(request.model_a, request.system_prompt, request.user_prompt),
            nim_client.call_model(request.model_b, request.system_prompt, request.user_prompt),
        )

        # Extract reasoning and final answers
        msg_a = response_a.get("choices", [{}])[0].get("message", {})
        msg_b = response_b.get("choices", [{}])[0].get("message", {})

        reasoning_a = extract_reasoning(msg_a)
        reasoning_b = extract_reasoning(msg_b)

        final_answer_a = msg_a.get("content", "").replace(reasoning_a, "").strip()
        final_answer_b = msg_b.get("content", "").replace(reasoning_b, "").strip()

        # Compute diff
        diff_result = diff_reasoning_chains(reasoning_a, reasoning_b)

        return DiffResponse(
            model_a=request.model_a,
            model_b=request.model_b,
            reasoning_a=reasoning_a,
            reasoning_b=reasoning_b,
            final_answer_a=final_answer_a,
            final_answer_b=final_answer_b,
            **diff_result,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)

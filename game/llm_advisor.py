from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from typing import Any


DEFAULT_MODEL_ID = os.getenv(
    "SOLD_EM_BEDROCK_MODEL",
    "us.anthropic.claude-3-5-haiku-20241022-v1:0",
)
DEFAULT_REGION = os.getenv("SOLD_EM_BEDROCK_REGION", "us-east-1")


def _build_prompt(state: dict[str, Any]) -> str:
    return (
        "You are an auction strategy assistant for a 5-player poker-auction game.\n"
        "Return strict JSON only, no markdown. Keys: bid, confidence, rationale, mode.\n"
        "bid must be integer >= 0 and <= stack.\n"
        "confidence in [0,1]. mode in {conservative,balanced,aggressive}.\n"
        "Use the provided deterministic recommendation as prior, but adjust for table dynamics.\n"
        f"STATE_JSON: {json.dumps(state, separators=(',', ':'))}"
    )


def _extract_text_response(raw: dict[str, Any]) -> str:
    content = raw.get("content", [])
    if not content:
        return ""
    first = content[0]
    if isinstance(first, dict):
        return str(first.get("text", ""))
    return str(first)


def _safe_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        if lines and lines[0].strip().lower() == "json":
            lines = lines[1:]
        text = "\n".join(lines).strip()

    try:
        out = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        out = json.loads(text[start : end + 1])
    if not isinstance(out, dict):
        raise ValueError("LLM output is not an object")
    return out


def _normalize_hint(raw: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    stack = max(0, int(state.get("stack", 0)))
    fair = max(0, int(state.get("fair_bid", 0)))

    bid = raw.get("bid", fair)
    try:
        bid = int(float(bid))
    except (TypeError, ValueError):
        bid = fair
    bid = max(0, min(stack, bid))

    confidence = raw.get("confidence", 0.5)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    mode = str(raw.get("mode", "balanced")).strip().lower()
    if mode not in {"conservative", "balanced", "aggressive"}:
        mode = "balanced"

    rationale = str(raw.get("rationale", "model_output")).strip()
    if not rationale:
        rationale = "model_output"
    if len(rationale) > 180:
        rationale = rationale[:180]

    return {
        "bid": bid,
        "confidence": confidence,
        "mode": mode,
        "rationale": rationale,
    }


def bedrock_llm_hint(
    state: dict[str, Any],
    *,
    model_id: str | None = None,
    region: str | None = None,
    timeout_sec: float = 8.0,
) -> dict[str, Any]:
    if os.getenv("SOLD_EM_LLM_DRY_RUN", "0") == "1":
        stack = int(state.get("stack", 0))
        fair = int(state.get("fair_bid", 0))
        return {
            "ok": True,
            "source": "dry_run",
            "model_id": model_id or DEFAULT_MODEL_ID,
            "latency_ms": 0,
            "hint": {
                "bid": max(0, min(stack, fair)),
                "confidence": 0.5,
                "rationale": "dry_run_stub",
                "mode": "balanced",
            },
        }

    model = model_id or DEFAULT_MODEL_ID
    reg = region or DEFAULT_REGION
    prompt = _build_prompt(state)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 160,
        "temperature": 0.0,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }

    with tempfile.TemporaryDirectory() as td:
        body_path = os.path.join(td, "body.json")
        out_path = os.path.join(td, "out.json")
        with open(body_path, "w", encoding="utf-8") as f:
            json.dump(body, f)

        cmd = [
            "aws",
            "bedrock-runtime",
            "invoke-model",
            "--region",
            reg,
            "--model-id",
            model,
            "--content-type",
            "application/json",
            "--accept",
            "application/json",
            "--body",
            f"fileb://{body_path}",
            out_path,
        ]
        start = time.perf_counter()
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                text=True,
            )
            latency_ms = int((time.perf_counter() - start) * 1000.0)
            with open(out_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            text = _extract_text_response(raw)
            out = _normalize_hint(_safe_json(text), state)
            return {
                "ok": True,
                "source": "bedrock",
                "model_id": model,
                "latency_ms": latency_ms,
                "hint": out,
            }
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - start) * 1000.0)
            return {
                "ok": False,
                "source": "bedrock",
                "model_id": model,
                "latency_ms": latency_ms,
                "error": str(exc),
            }

#!/usr/bin/env bash
set -euo pipefail

REGION="${1:-us-east-1}"
MODEL_ID="${2:-us.anthropic.claude-3-5-haiku-20241022-v1:0}"
N_CALLS="${3:-3}"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

BODY_PATH="$TMPDIR/body.json"
cat >"$BODY_PATH" <<'JSON'
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 64,
  "temperature": 0.0,
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "You are a trading assistant. Reply only with: 42"}
      ]
    }
  ]
}
JSON

echo "region=$REGION model_id=$MODEL_ID calls=$N_CALLS"

total_ms=0
for i in $(seq 1 "$N_CALLS"); do
  out_path="$TMPDIR/out_$i.json"
  start_ms=$(date +%s%3N)
  aws bedrock-runtime invoke-model \
    --region "$REGION" \
    --model-id "$MODEL_ID" \
    --content-type application/json \
    --accept application/json \
    --body "fileb://$BODY_PATH" \
    "$out_path" >/dev/null
  end_ms=$(date +%s%3N)
  dt=$((end_ms - start_ms))
  total_ms=$((total_ms + dt))
  echo "call_$i latency_ms=$dt"
done

avg_ms=$((total_ms / N_CALLS))
echo "avg_latency_ms=$avg_ms"

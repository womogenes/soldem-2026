#!/usr/bin/env bash
set -euo pipefail

REGION="us-east-1"
BUCKET=""
PREFIX="artifacts/hud"
OUT_KEY=""
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --bucket) BUCKET="$2"; shift 2;;
    --prefix) PREFIX="$2"; shift 2;;
    --out-key) OUT_KEY="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$BUCKET" ]]; then
  echo "Missing required --bucket"
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"
GIT_SHA="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo nogit)"
if [[ -z "$OUT_KEY" ]]; then
  OUT_KEY="${PREFIX}/soldem_hud_${TS}_${GIT_SHA}.tar.gz"
fi

TMP_TAR="/tmp/$(basename "$OUT_KEY")"
echo "Packaging artifact at $TMP_TAR"
tar -C "$ROOT_DIR" -czf "$TMP_TAR" \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='web/node_modules' \
  --exclude='web/.svelte-kit' \
  --exclude='web/build' \
  --exclude='research_logs/experiment_outputs/distributed_*' \
  --exclude='research_logs/aws_worker_map_*' \
  .

echo "Uploading to s3://$BUCKET/$OUT_KEY"
aws s3 cp "$TMP_TAR" "s3://$BUCKET/$OUT_KEY" --region "$REGION"

echo "ARTIFACT_KEY=$OUT_KEY"
echo "ARTIFACT_URI=s3://$BUCKET/$OUT_KEY"
echo "LOCAL_TAR=$TMP_TAR"

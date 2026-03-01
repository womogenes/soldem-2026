#!/usr/bin/env bash
set -euo pipefail

REGION="us-east-1"
HOST=""
USER_NAME="ec2-user"
SSH_KEY_PATH="$HOME/.codex/.ssh/id_ed25519"
BUCKET=""
ARTIFACT_KEY=""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --host) HOST="$2"; shift 2;;
    --user) USER_NAME="$2"; shift 2;;
    --ssh-key-path) SSH_KEY_PATH="$2"; shift 2;;
    --bucket) BUCKET="$2"; shift 2;;
    --artifact-key) ARTIFACT_KEY="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$HOST" ]]; then
  echo "Missing required --host"
  exit 1
fi
if [[ -z "$BUCKET" ]]; then
  echo "Missing required --bucket"
  exit 1
fi
if [[ ! -f "$SSH_KEY_PATH" ]]; then
  echo "SSH private key not found: $SSH_KEY_PATH"
  exit 1
fi

if [[ -z "$ARTIFACT_KEY" ]]; then
  PUB_OUT="$(bash "$ROOT_DIR/scripts/aws/publish_hud_artifact.sh" --region "$REGION" --bucket "$BUCKET")"
  echo "$PUB_OUT"
  ARTIFACT_KEY="$(printf '%s\n' "$PUB_OUT" | awk -F= '/^ARTIFACT_KEY=/{print $2}')"
fi
if [[ -z "$ARTIFACT_KEY" ]]; then
  echo "Could not resolve ARTIFACT_KEY"
  exit 1
fi

LOCAL_TAR="/tmp/$(basename "$ARTIFACT_KEY")"
if [[ ! -f "$LOCAL_TAR" ]]; then
  aws s3 cp "s3://$BUCKET/$ARTIFACT_KEY" "$LOCAL_TAR" --region "$REGION"
fi

scp -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$LOCAL_TAR" "$USER_NAME@$HOST:/tmp/soldem_hud_release.tar.gz"
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$USER_NAME@$HOST" "sudo bash -s" <<'REMOTE'
set -euxo pipefail
alternatives --set node /usr/bin/node-20 >/dev/null 2>&1 || true
if ! command -v pnpm >/dev/null 2>&1; then
  npm install -g pnpm
fi
/opt/soldem/bin/deploy_release.sh /tmp/soldem_hud_release.tar.gz
REMOTE

HEALTH=""
for _ in $(seq 1 30); do
  if HEALTH="$(curl -fsS "http://$HOST/api/health" 2>/dev/null)"; then
    break
  fi
  sleep 2
done
if [[ -z "$HEALTH" ]]; then
  echo "Health check failed: http://$HOST/api/health"
  exit 1
fi
echo "Updated stack health: $HEALTH"
echo "HUD_URL=http://$HOST"
echo "API_HEALTH=http://$HOST/api/health"
echo "ARTIFACT_KEY=$ARTIFACT_KEY"

#!/usr/bin/env bash
set -euo pipefail

REGION="us-east-1"
INSTANCE_TYPE="t3.large"
KEY_NAME="codex-soldem-ed25519"
SSH_KEY_PATH="$HOME/.codex/.ssh/id_ed25519"
USER_NAME="ec2-user"
ALLOW_CIDR="0.0.0.0/0"
NAME="soldem-hud-main"
SG_NAME="soldem-hud-sg"
BUCKET=""
ARTIFACT_KEY=""
ASSOCIATE_EIP="true"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --instance-type) INSTANCE_TYPE="$2"; shift 2;;
    --key-name) KEY_NAME="$2"; shift 2;;
    --ssh-key-path) SSH_KEY_PATH="$2"; shift 2;;
    --user) USER_NAME="$2"; shift 2;;
    --allow-cidr) ALLOW_CIDR="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --sg-name) SG_NAME="$2"; shift 2;;
    --bucket) BUCKET="$2"; shift 2;;
    --artifact-key) ARTIFACT_KEY="$2"; shift 2;;
    --associate-eip) ASSOCIATE_EIP="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

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

VPC_ID="$(aws ec2 describe-vpcs --region "$REGION" --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)"
SUBNET_ID="$(aws ec2 describe-subnets --region "$REGION" --filters Name=default-for-az,Values=true --query 'Subnets[0].SubnetId' --output text)"

SG_ID="$(aws ec2 describe-security-groups --region "$REGION" --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)"
if [[ -z "$SG_ID" || "$SG_ID" == "None" ]]; then
  SG_ID="$(aws ec2 create-security-group --region "$REGION" --group-name "$SG_NAME" --description "Soldem HUD SG" --vpc-id "$VPC_ID" --query 'GroupId' --output text)"
fi
aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 22 --cidr "$ALLOW_CIDR" 2>/dev/null || true
aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 80 --cidr "$ALLOW_CIDR" 2>/dev/null || true

AMI_ID="$(aws ssm get-parameter --region "$REGION" --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query 'Parameter.Value' --output text)"

INSTANCE_ID="$(aws ec2 run-instances \
  --region "$REGION" \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --subnet-id "$SUBNET_ID" \
  --associate-public-ip-address \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=Project,Value=soldem-hud}]" \
  --query 'Instances[0].InstanceId' \
  --output text)"

echo "Launched instance: $INSTANCE_ID"
aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"

PUBLIC_IP="$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)"

if [[ "$ASSOCIATE_EIP" == "true" ]]; then
  ALLOC_ID="$(aws ec2 allocate-address --region "$REGION" --domain vpc --query 'AllocationId' --output text)"
  aws ec2 associate-address --region "$REGION" --instance-id "$INSTANCE_ID" --allocation-id "$ALLOC_ID" >/dev/null
  PUBLIC_IP="$(aws ec2 describe-addresses --region "$REGION" --allocation-ids "$ALLOC_ID" --query 'Addresses[0].PublicIp' --output text)"
  echo "Associated Elastic IP: $PUBLIC_IP ($ALLOC_ID)"
fi

echo "Waiting for SSH on $PUBLIC_IP..."
for _ in $(seq 1 60); do
  if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "$SSH_KEY_PATH" "$USER_NAME@$PUBLIC_IP" 'echo ok' >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

LOCAL_TAR="/tmp/$(basename "$ARTIFACT_KEY")"
if [[ ! -f "$LOCAL_TAR" ]]; then
  aws s3 cp "s3://$BUCKET/$ARTIFACT_KEY" "$LOCAL_TAR" --region "$REGION"
fi

scp -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$LOCAL_TAR" "$USER_NAME@$PUBLIC_IP:/tmp/soldem_hud_release.tar.gz"

ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$USER_NAME@$PUBLIC_IP" "sudo bash -s" <<'REMOTE'
set -euxo pipefail
dnf install -y nginx python3 tar gzip git
if dnf info nodejs20 >/dev/null 2>&1; then
  dnf install -y nodejs20
else
  curl -fsSL https://rpm.nodesource.com/setup_22.x | bash -
  dnf install -y nodejs
fi
alternatives --set node /usr/bin/node-20 >/dev/null 2>&1 || true
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
npm install -g pnpm

mkdir -p /opt/soldem/bin /opt/soldem/releases

cat >/opt/soldem/bin/deploy_release.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

TAR_PATH="${1:-/tmp/soldem_hud_release.tar.gz}"
APP_ROOT="/opt/soldem/app"
TMP_ROOT="/opt/soldem/releases/app_new"
UV_BIN="/root/.local/bin/uv"
if [[ ! -x "$UV_BIN" ]]; then
  UV_BIN="/home/ec2-user/.local/bin/uv"
fi
if [[ ! -x "$UV_BIN" ]]; then
  echo "uv binary not found"
  exit 1
fi

rm -rf "$TMP_ROOT"
mkdir -p "$TMP_ROOT"
tar -xzf "$TAR_PATH" -C "$TMP_ROOT"
rm -rf "${APP_ROOT}.prev"
if [[ -d "$APP_ROOT" ]]; then
  mv "$APP_ROOT" "${APP_ROOT}.prev"
fi
mv "$TMP_ROOT" "$APP_ROOT"

cd "$APP_ROOT"
"$UV_BIN" sync
PNPM_BIN="$(command -v pnpm || true)"
if [[ -z "$PNPM_BIN" && -x /usr/bin/pnpm ]]; then
  PNPM_BIN="/usr/bin/pnpm"
fi
if [[ -z "$PNPM_BIN" ]]; then
  echo "pnpm binary not found"
  exit 1
fi
"$PNPM_BIN" -C web install --frozen-lockfile
"$PNPM_BIN" -C web build

cat >/etc/systemd/system/soldem-backend.service <<'SERVICE'
[Unit]
Description=Soldem backend API
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/soldem/app
Environment=SOLDEM_POLICY_PATH=/opt/soldem/app/research_logs/experiment_outputs/dayof_policy_cross_branch_reconciled_v12.json
ExecStart=/root/.local/bin/uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

cat >/etc/systemd/system/soldem-frontend.service <<'SERVICE'
[Unit]
Description=Soldem frontend HUD
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/soldem/app
Environment=VITE_API_BASE=/api
ExecStart=/usr/bin/pnpm -C web preview --host 127.0.0.1 --port 4173
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

cat >/etc/nginx/conf.d/soldem-hud.conf <<'NGINX'
server {
  listen 80 default_server;
  server_name soldem-hud.local;

  location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location / {
    proxy_pass http://127.0.0.1:4173;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
NGINX

nginx -t
systemctl daemon-reload
systemctl enable --now soldem-backend soldem-frontend nginx
systemctl restart soldem-backend soldem-frontend nginx
SCRIPT

chmod +x /opt/soldem/bin/deploy_release.sh
/opt/soldem/bin/deploy_release.sh /tmp/soldem_hud_release.tar.gz
REMOTE

HEALTH=""
for _ in $(seq 1 30); do
  if HEALTH="$(curl -fsS "http://$PUBLIC_IP/api/health" 2>/dev/null)"; then
    break
  fi
  sleep 2
done
if [[ -z "$HEALTH" ]]; then
  echo "Health check failed: http://$PUBLIC_IP/api/health"
  exit 1
fi
echo "Remote health: $HEALTH"

RUN_TS="$(date +%Y%m%d-%H%M%S)"
OUT_JSON="$ROOT_DIR/research_logs/aws_hud_deploy_${RUN_TS}.json"
cat >"$OUT_JSON" <<JSON
{
  "region": "$REGION",
  "instance_id": "$INSTANCE_ID",
  "public_ip": "$PUBLIC_IP",
  "bucket": "$BUCKET",
  "artifact_key": "$ARTIFACT_KEY",
  "ssh_user": "$USER_NAME",
  "ssh_key_path": "$SSH_KEY_PATH"
}
JSON

echo "DEPLOY_METADATA=$OUT_JSON"
echo "HUD_URL=http://$PUBLIC_IP"
echo "API_HEALTH=http://$PUBLIC_IP/api/health"

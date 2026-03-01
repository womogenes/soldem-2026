# Cloud setup for PocketBase and workers

Local timestamp: 2026-03-01 01:45:00 PST

## Current live PocketBase

- `instance_id`: `i-08f41ea7a4d11aaca`
- `public_ip`: `44.221.42.217`
- `url`: `http://44.221.42.217:8090`
- Region: `us-east-1`

## Bootstrap collections

```bash
uv run python scripts/pocketbase_bootstrap.py \
  --base-url http://44.221.42.217:8090 \
  --admin-email <ADMIN_EMAIL> \
  --admin-password <ADMIN_PASSWORD>
```

## Sync experiment outputs

```bash
uv run python scripts/sync_experiments_to_pocketbase.py \
  --base-url http://44.221.42.217:8090 \
  --admin-email <ADMIN_EMAIL> \
  --admin-password <ADMIN_PASSWORD> \
  --glob 'research_logs/experiment_outputs/candidates_*.json'
```

## Worker heartbeat check

```bash
TOKEN=$(uv run python - <<'PY'
import json, urllib.request
base='http://44.221.42.217:8090'
req=urllib.request.Request(
    f'{base}/api/collections/_superusers/auth-with-password',
    data=json.dumps({'identity':'<ADMIN_EMAIL>','password':'<ADMIN_PASSWORD>'}).encode(),
    headers={'content-type':'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as r:
    print(json.loads(r.read().decode())['token'])
PY
)
uv run python scripts/worker_heartbeat.py \
  --base-url http://44.221.42.217:8090 \
  --admin-token "$TOKEN" \
  --worker-id local-test-001 \
  --role sim \
  --status running
```

## Launch worker swarm

```bash
scripts/aws/launch_worker_swarm.sh \
  --key-name codex-soldem-ed25519 \
  --repo <git-url> \
  --branch main \
  --pocketbase-url http://44.221.42.217:8090 \
  --admin-token <superuser-jwt> \
  --count 4
```

## Cost guardrails

- Use small worker counts first.
- Terminate idle EC2 instances immediately after runs.
- Check daily spend before scaling:

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d 'today' +%Y-%m-%d),End=$(date -d 'tomorrow' +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost
```

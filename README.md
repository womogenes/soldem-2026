# Sold 'Em v2 research and HUD

This branch contains the overnight research, simulation, policy-search, and HUD/API integration work for day-of play.

## What is in this branch

- Rule-profile aware engine and ranking policies (`game/`).
- Strategy framework with parameterized specs and built-in families (`strategies/`).
- Simulation and matrix tooling for long replicated runs (`sim/`, `scripts/`).
- Research artifacts and policy maps (`research_logs/experiment_outputs/`).
- Live advisor API + HUD with correlation inference and auto policy-condition routing (`game/api.py`, `web/`).
- Runbooks and handoff docs for day-of operation and fast rule patching (`docs/`).

## Current day-of default

- Primary policy map:
  - `research_logs/experiment_outputs/dayof_policy_cross_branch_reconciled_v12.json`
- Default objective mapping in that policy:
  - `ev -> seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2`
  - `first_place -> meta_switch_v4`
  - `robustness -> seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2`
- Fast handoff reference:
  - `docs/07am_handoff_summary.md`

## Quickstart

### Backend

```bash
SOLDEM_POLICY_PATH=research_logs/experiment_outputs/dayof_policy_cross_branch_reconciled_v12.json \
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

### HUD

```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

### Tests and checks

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
pnpm --dir web check
```

## AWS deployment

This repo now includes full-stack deploy/update scripts for a single EC2 host running:

- Backend API (`uvicorn`) on `127.0.0.1:8000`
- HUD frontend (`pnpm preview`) on `127.0.0.1:4173`
- `nginx` on port `80` with:
  - `/api/*` -> backend
  - `/*` -> frontend

### One-time deploy

```bash
scripts/aws/deploy_hud_stack_ec2.sh \
  --bucket soldem-2026-539881456097-1772358537 \
  --key-name codex-soldem-ed25519 \
  --instance-type t3.large \
  --name soldem-hud-main
```

What this does:

1. Publishes a code artifact to S3.
2. Creates/uses security group `soldem-hud-sg` (opens `22` and `80`).
3. Launches EC2 and associates an Elastic IP.
4. Installs runtime dependencies (`uv`, Node 20, pnpm, nginx).
5. Deploys backend + frontend as systemd services.
6. Validates `http://<ip>/api/health`.

### Updating backend and frontend in one command

After code changes, run:

```bash
scripts/aws/update_hud_stack_ec2.sh \
  --bucket soldem-2026-539881456097-1772358537 \
  --host 34.233.242.212
```

This updates both backend and frontend together by:

1. Publishing a fresh artifact to S3.
2. Copying it to the host over SSH.
3. Rebuilding Python + web deps.
4. Rebuilding frontend.
5. Restarting backend/frontend/nginx.
6. Waiting for `/api/health` to pass.

### Current deployed stack

- HUD URL: `http://34.233.242.212`
- API health: `http://34.233.242.212/api/health`
- Deploy metadata:
  - `research_logs/aws_hud_deploy_20260301-080700.json`

### Service operations on host

```bash
ssh -i ~/.codex/.ssh/id_ed25519 ec2-user@34.233.242.212
sudo systemctl status soldem-backend soldem-frontend nginx
sudo journalctl -u soldem-backend -n 200 --no-pager
sudo journalctl -u soldem-frontend -n 200 --no-pager
```

### If you need to redeploy with a fixed artifact

```bash
scripts/aws/update_hud_stack_ec2.sh \
  --bucket soldem-2026-539881456097-1772358537 \
  --host 34.233.242.212 \
  --artifact-key artifacts/hud/<artifact>.tar.gz
```

### Security notes

- Restrict `--allow-cidr` in `deploy_hud_stack_ec2.sh` for production usage.
- Add TLS (ACM + ALB or certbot on-instance) if this is used beyond internal testing.
- Rotate keys and lock down SG ingress before competition day.

## Key docs

- Day-of operations:
  - `docs/day_of_runbook.md`
- 7 am handoff:
  - `docs/07am_handoff_summary.md`
- Research execution workflow:
  - `docs/research_runbook.md`
- Rule variation rapid patching:
  - `docs/day_of_patch_guide.md`
- Research-backed strategy rationale:
  - `research/research_backed_strategy_playbook.md`
- Timeline log:
  - `research_logs/2026-03-01_live_log.md`

## Reconcile other worktrees

Use this process when another worktree/agent generates new experiment outputs.

1. Put all new outputs in `research_logs/experiment_outputs/` with timestamped names.
2. Analyze long-matrix results:
```bash
python scripts/analyze_long_matrix.py \
  --input research_logs/experiment_outputs/long_parallel_matrix_<timestamp>.json
```
3. Build per-run policy map (mean and LCB):
```bash
python scripts/build_dayof_policy.py \
  --analysis research_logs/experiment_outputs/long_parallel_matrix_<timestamp>.analysis.json \
  --winner-mode lcb \
  --out research_logs/experiment_outputs/dayof_policy_<timestamp>_lcb.json
```
4. Merge policy maps with clear precedence (later overrides earlier):
```bash
python scripts/merge_policy_maps.py \
  research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json \
  research_logs/experiment_outputs/dayof_policy_<timestamp>_lcb.json \
  --default-from research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json \
  --out research_logs/experiment_outputs/dayof_policy_hybrid_v12_lcb.json
```
5. Validate before promotion:
```bash
python -m unittest discover -s tests -p 'test_*.py' -v
pnpm --dir web check
```
6. Promote in `game/api.py` by placing the new file at the top of `_auto_load_policy()` candidate list.
7. Update `docs/07am_handoff_summary.md`, `docs/day_of_runbook.md`, and `research_logs/2026-03-01_live_log.md`.

## Key code paths

- Engine: `game/engine_base.py`
- Rules: `game/rules.py`
- Hand evaluator: `game/utils.py`
- Advisor: `game/advisor.py`
- API: `game/api.py`
- Correlation inference: `game/correlation.py`
- Strategies: `strategies/`
- Simulation: `sim/`
- Experiment scripts: `scripts/`
- Research artifacts: `research/`, `research_logs/`

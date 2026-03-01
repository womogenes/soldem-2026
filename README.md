# Sold 'Em 2026 v5

## Project overview

This branch contains the overnight strategy-search and deployment work for Sold 'Em. It includes:

- game engine and API (`game/`)
- strategy families and loaders (`strategies/`)
- simulation + evaluation tooling (`sim/`, `scripts/`)
- web HUD (`web/`)
- EC2/AWS experiment artifacts and run logs (`research_logs/`)

`RULES.md` is the source of truth for game behavior.

## Current promoted strategy state

As of the latest promoted artifact, the active objective split is:

- `ev`: `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
- `first_place`: `seller_profit`
- `robustness`: `seller_extraction:opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2`

Canonical artifact:

- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-071000-merged4.json`

Fast verification:

```bash
uv run python scripts/print_latest_champions.py
```

## What changed overnight

Major additions and upgrades:

- Distributed EC2 tournament pipeline (`launch_distributed_experiments.sh` + collectors).
- EC2 param-sweep and evolution pipelines.
- Objective-strength analytics in distributed summarization (`scripts/aws/summarize_distributed_champions.py`).
- Day-of fast patch helper (`scripts/day_of/apply_rule_variation.py`).
- PocketBase AWS sync pipeline and runbooks.
- Multiple promoted upgrade artifacts culminating in merged4 (`n_scenarios=864`).

Key commit spine from the session:

- `6456979` through `63c9bb6` (see `git log --oneline`).
- Latest branch tip should include merged4 promotion and post-7am update docs.

## Runtime quick start

Backend:

```bash
uv run uvicorn game.api:app --reload --host 0.0.0.0 --port 8000
```

HUD:

```bash
cd web
pnpm install
pnpm dev --host 0.0.0.0 --port 4173
```

Load latest promoted champions into API state:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path": null}'
```

## Worktree reconciliation guide

Use this when merging other worktrees/branches back into this state.

1. Fetch and inspect branch tip.

```bash
git fetch origin
git log --oneline --decorate --graph origin/v5 -n 30
```

2. Merge or rebase your worktree branch onto `v5`.

```bash
git checkout <your-branch>
git merge origin/v5
# or: git rebase origin/v5
```

3. Resolve conflicts with these priorities.

- Keep `RULES.md` as source of truth.
- Keep latest promoted champion artifact precedence in `game/champion_loader.py`.
- Keep API/champion defaults aligned with `scripts/print_latest_champions.py` output.
- Preserve overnight runbook/docs in `research_logs/` (do not drop latest execution context).

4. Re-validate locally.

```bash
uv run python -m unittest discover -s tests -v
cd web && pnpm build && cd ..
uv run python scripts/print_latest_champions.py
```

5. Confirm reconciliation outputs.

- `scripts/print_latest_champions.py` points at merged4 (or a newer promoted artifact if intentionally updated).
- No stale worker fleets remain if you ran AWS experiments.

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters Name=instance-state-name,Values=pending,running,stopping,stopped Name=tag:Project,Values=soldem-dist,soldem-evolution,soldem-param-sweep \
  --query 'length(Reservations[])' --output text
```

## Canonical docs

Read these first before making day-of changes:

- `research_logs/2026-03-01_pre7am_summary.md`
- `research_logs/2026-03-01_post7am_update.md`
- `research_logs/2026-03-01_system_summary.md`
- `research_logs/2026-03-01_human_playbook.md`
- `research_logs/2026-03-01_quick_reference_card.md`
- `research_logs/2026-03-01_mode_switch_policy.md`
- `research_logs/2026-03-01_day_of_patch_guide.md`
- `research_logs/2026-03-01_aws_distributed_runbook.md`
- `research_logs/2026-03-01_execution_log.md`

Spec anchor for future compaction/rollouts:

- `research_logs/000_god_prompt.md`

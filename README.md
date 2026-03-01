# Sold 'Em 2026 day-of system

## Overview

This repository contains the overnight strategy-research and operator stack for the Sold 'Em event.

The active day-of architecture is:
- simulation and rollout engine (`sim/`, `strategies/`)
- advisor backend API (`game/api.py`)
- operator HUD (`web/`)
- day-of patch and autosolve tooling (`scripts/day_of_patch.py`, `scripts/day_of_autosolve_patch.py`)
- preflight and smoke checks (`scripts/day_of_preflight.sh`, `scripts/policy_smoke.py`, `scripts/advisor_smoke.py`)

The controlling spec that drove the overnight work is:
- `research_logs/000_god_prompt.md`

## Current status

As of the latest overnight checkpoint, this branch (`v4`) has:
- dynamic first-place routing tuned for baseline and winner-takes-all variants
- correlated-pair defensive override for first-place routing
- non-5-player support in solver/sim/API/HUD paths
- advisor request normalization against active rule profile bounds
- champion recompute honoring active rule overrides
- full day-of runbooks and handoff docs in `research_logs/`

Primary strategy defaults:
- `ev`: `equity_evolved_v1`
- `robustness`: `equity_evolved_v1`
- `first_place`: dynamic routing by profile and table-read cues

## Quick start

1. Install deps:
```bash
uv sync
pnpm -C web install
```

2. Start backend:
```bash
uv run uvicorn game.api:app --host 0.0.0.0 --port 8000
```

3. Start HUD:
```bash
pnpm -C web dev --host
```

4. Optional baseline preflight:
```bash
bash scripts/day_of_preflight.sh \
  --api-url http://127.0.0.1:8000 \
  --with-policy-smoke \
  --with-advisor-smoke
```

## Day-of operations

Apply announced rules quickly:
```bash
uv run python scripts/day_of_patch.py --preset baseline --overrides-json '<json>'
```

Optional quick empirical lock:
```bash
uv run python scripts/day_of_autosolve_patch.py \
  --rule-profile baseline_v1 \
  --overrides-json '<json>' \
  --n-tables 12 \
  --n-games 8 \
  --seed 42
```

If you want to keep dynamic resolver behavior after autosolve:
```bash
uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --keep-dynamic
```

## Worktree reconciliation

If you have multiple local worktrees or parallel branches, use this section to reconcile safely.

Recommended (single-step):
```bash
git fetch origin
git checkout <your-branch>
git merge --no-ff origin/v4
```

If you must cherry-pick instead of merging, use this minimum operational chain (in order):
1. `930cced` HUD supports dynamic `n_players` inputs.
2. `bee4a15` Correlated-pair defensive first-place override.
3. `5ef9e69` Session/profile `n_players` sync and expanded policy smoke.
4. `01ee7da` Advisor request normalization to active rule-profile bounds.
5. `5a3bd7c` Recompute champions uses active rule overrides.
6. `added02` Advisor normalization smoke script + preflight hook.

Cherry-pick example:
```bash
git fetch origin
git checkout <your-branch>
git cherry-pick 930cced bee4a15 5ef9e69 01ee7da 5a3bd7c added02
```

After merge/cherry-pick, run validation:
```bash
uv run -m unittest discover -s tests -v
pnpm -C web check
bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --with-policy-smoke --with-advisor-smoke
```

## Key logs and handoff docs

Read these first if you are resuming from another worktree:
- `research_logs/021_pre7_summary.md`
- `research_logs/013_pre7_handoff_draft.md`
- `research_logs/004_status_snapshot.md`
- `research_logs/003_day_of_fast_patch_guide.md`
- `research_logs/001_night_rollout_log.md`

High-value artifact folder:
- `research_logs/experiment_outputs/`

## Testing

Backend:
```bash
uv run -m unittest discover -s tests -v
```

Web:
```bash
pnpm -C web check
pnpm -C web build
```

Targeted policy smoke:
```bash
uv run python scripts/policy_smoke.py --api http://127.0.0.1:8000
```

Targeted advisor normalization smoke:
```bash
uv run python scripts/advisor_smoke.py --api http://127.0.0.1:8000
```

## Notes

- `RULES.md` is source of truth for game rules.
- Some historical utilities may not match rule truth; use `RULES.md` and validated engine behavior.
- Keep research logs timestamped in local time in `research_logs/` for continuity across agent rollouts.

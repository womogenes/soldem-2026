# Sold 'Em v3 strategy lab and HUD

This repository contains a full loop for Sold 'Em strategy research:

- Rule-profile game engine and hand evaluator
- Pluggable strategy interface (tags and Python files)
- Population simulation and experiment matrix tooling
- FastAPI live advisor backend
- Svelte HUD for rapid in-game state entry
- PocketBase integration for strategy/eval tracking

Current high-confidence defaults:

- `ev`: `market_maker_v2`
- `first_place` (safe default): `market_maker_v2`
- `robustness`: `regime_switch_v2`
- `tournament_win`: `market_maker_v2`
- Optional high-variance first-place override: `pot_fraction`

## Quickstart

### Backend

```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

### HUD

```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

### Tests

```bash
uv run python -m unittest discover -s tests -q
```

## Key docs

- [Rule assumptions](docs/rule_assumptions.md)
- [Strategy format](docs/strategy_format.md)
- [Champion results](docs/champion_results.md)
- [Day-of runbook](docs/day_of_runbook.md)
- [Day-of patch guide](docs/day_of_patch_guide.md)
- [Cloud setup](docs/cloud_setup.md)
- [Literature review](research_logs/literature_auction_poker_imperfect_info_2026-03-01.md)

## Reconcile parallel worktrees

Use this section to merge work from `../v2`, EC2 workers, or other local worktrees without losing the 7am baseline.

Canonical branch and commits:

- Branch: `v3` (remote `origin/v3`)
- Baseline integration: `f7f6f5c` (`Add 7am tournament horizon/profile validations and tie-break artifacts`)
- Latest push: `4db8be9` (`Add broad tournament-win parameter search artifact`)

Canonical outcome at 7am PST (2026-03-01):

- Keep defaults: `market_maker_v2` for `ev`, `first_place` (safe), and `tournament_win`
- Keep `regime_switch_v2` for `robustness`
- Keep `pot_fraction` only as explicit high-variance override

Canonical artifacts to preserve when reconciling:

- `research_logs/2026-03-01_research_log.md`
- `research_logs/2026-03-01_7am_handoff_summary.md`
- `research_logs/experiment_outputs/finalists_long_*.json`
- `research_logs/experiment_outputs/finalists_*tournament_win*.json`
- `research_logs/experiment_outputs/tournament_win_horizon_fastlong.json`
- `research_logs/experiment_outputs/rule_profile_tournament_win_fastlong.json`
- `research_logs/experiment_outputs/rule_profile_tournament_win_tiebreak.json`
- `research_logs/champion_lookup_from_*`

Merge checklist for incoming worktree changes:

1. Rebase/cherry-pick onto `v3`.
2. Re-run `uv run python -m unittest discover -s tests -q`.
3. Re-run `pnpm --dir web check`.
4. If strategy defaults change, regenerate champion lookup files and update:
   - `game/api.py` (`PROFILE_OBJECTIVE_DEFAULTS`)
   - `docs/champion_results.md`
   - `research_logs/2026-03-01_7am_handoff_summary.md`
5. Append a timestamped entry in `research_logs/2026-03-01_research_log.md`.

## Critical reference for future rollouts

Always include `research_logs/000_god_prompt.md` during compaction/handoff.

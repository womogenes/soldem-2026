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

## Critical reference for future rollouts

Always include `research_logs/000_god_prompt.md` during compaction/handoff.

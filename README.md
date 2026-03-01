# Sold 'Em v2 research and HUD

This repository now includes:

- Rule-profile driven game engine
- Rarity-based and standard ranking policies
- Pluggable strategy framework (built-ins + external Python files)
- Population simulation and experiment matrix tooling
- Live FastAPI advisor backend
- Rebuilt Svelte HUD for rapid in-game use
- Day-of patch and runbook documentation

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
python -m unittest discover -s tests -p 'test_*.py' -v
pnpm --dir web check
```

## Key paths

- Engine: `game/engine_base.py`
- Rules: `game/rules.py`
- Hand evaluator: `game/utils.py`
- Advisor: `game/advisor.py`
- API: `game/api.py`
- Strategies: `strategies/`
- Simulation: `sim/`
- Scripts: `scripts/`
- Docs: `docs/`
- Logs: `research_logs/`

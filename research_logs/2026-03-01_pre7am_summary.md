# Pre-7am handoff summary

Local timestamp: 2026-03-01 06:45:34 PST

## Final promoted strategy set

- Active artifact: `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json`
- Active objective champions:
- `ev`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- `first_place`: `seller_profit`
- `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`

## Why this is final

- Human-focused merged distributed evidence (`053816` + `061228`, 432 scenarios) briefly favored `5400/0.032/2` for `ev`.
- Quick exploitability sweep against `5400/0.032/2` (`param_sweep_20260301-063621`) showed multiple challengers with positive mean delta vs 5400.
- Conservative pre-7am rollback selected `4400/0.02/2` as safer EV/robustness baseline while retaining `seller_profit` for first-place pushes.

## What to run day-of

1. Start backend:

```bash
uv run uvicorn game.api:app --reload --host 0.0.0.0 --port 8000
```

2. Start HUD:

```bash
cd web
pnpm install
pnpm dev --host 0.0.0.0 --port 4173
```

3. Force-load latest champions:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path": null}'
```

4. Verify loaded champions:

```bash
uv run python scripts/print_latest_champions.py
```

5. If rules change, apply and recompute quickly:

```bash
uv run python scripts/day_of/apply_rule_variation.py \
  --profile-name baseline_v1 \
  --overrides-json '{"n_orbits":4}' \
  --n-matches 35 \
  --n-games-per-match 8 \
  --seed 20260301
```

## Key docs

- System overview: `research_logs/2026-03-01_system_summary.md`
- Human playbook: `research_logs/2026-03-01_human_playbook.md`
- Quick card: `research_logs/2026-03-01_quick_reference_card.md`
- Day-of patch flow: `research_logs/2026-03-01_day_of_patch_guide.md`
- AWS operations: `research_logs/2026-03-01_aws_distributed_runbook.md`
- Full execution timeline: `research_logs/2026-03-01_execution_log.md`

## Spec anchor for future compaction

- Keep `research_logs/000_god_prompt.md` referenced as the top-level project spec.

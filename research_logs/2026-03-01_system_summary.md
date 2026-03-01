# Sold 'Em system summary

Local timestamp: 2026-03-01 01:45:55 PST

## What is ready now

- Verified rules/engine alignment and recomputed full hand rarity counts for the 50-card deck.
- Implemented parameterized strategy loading with spec strings (for example `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`).
- Added advanced strategy family:
- `prob_value`
- `risk_sniper`
- `seller_extraction`
- Ran evolutionary search and broad validation (objective, horizon, correlation, rule-profile variants).
- Integrated winning strategy as default champion in API/HUD flow.
- Added PocketBase sync tooling and improved AWS worker launch script for remote batch jobs.
- Added day-of rapid rule-variation patch runbook.
- Backend and web UI both pass smoke checks/build checks.

## Best current strategy

- Champion spec:
- `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`
- It won all tested matrix slices in this rollout:
- objective: `ev`, `first_place`, `robustness`
- horizons: `5`, `10`, `20`
- correlations: `none`, `respect`, `herd`, `kingmaker`
- rule profiles: `baseline_v1`, `standard_rankings`, `seller_self_bid`, `top2_split`, `high_low_split`, `single_card_sell`
- Additional EC2 distributed confirmation:
- run `20260301-015615` (216 scenarios): champion won 160
- run `20260301-020134` (216 scenarios, `n_matches=120`): champion won 199
- run `20260301-021037` (216 scenarios, `n_matches=250`): champion won 212
- combined distributed total: champion won 571 / 648 scenarios

## Key artifacts

- Execution timeline log: `research_logs/2026-03-01_execution_log.md`
- Literature review: `research_logs/2026-03-01_literature_review.md`
- Day-of patch guide: `research_logs/2026-03-01_day_of_patch_guide.md`
- Human playbook: `research_logs/2026-03-01_human_playbook.md`
- AWS distributed runbook: `research_logs/2026-03-01_aws_distributed_runbook.md`
- Strategy format: `strategies/strategy_format.md`
- Baseline tournament output: `research_logs/experiment_outputs/baseline_population_seed42.json`
- Evolution outputs:
- `research_logs/experiment_outputs/evolution_runs.jsonl`
- `research_logs/experiment_outputs/evolution_summary.json`
- Robustness matrices:
- `research_logs/experiment_outputs/champion_validation_matrix.json`
- `research_logs/experiment_outputs/rule_profile_validation.json`
- `research_logs/experiment_outputs/large_validation_baseline_respect.json`
- `research_logs/experiment_outputs/precomputed_variation_champions.json`
- `research_logs/experiment_outputs/distributed_20260301-015615/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-020134/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-015615.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-020134.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-021037.json`
- `research_logs/experiment_outputs/distributed_master_summary_20260301.json`

## Run instructions

### Backend

```bash
uv run uvicorn game.api:app --reload --host 0.0.0.0 --port 8000
```

### Web HUD

```bash
cd web
pnpm install
pnpm dev --host 0.0.0.0 --port 4173
```

### Recompute champions

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/recompute_champions \
  -H 'content-type: application/json' \
  -d '{"n_matches": 60, "n_games_per_match": 10, "seed": 12345}'
```

### Run evolutionary search

```bash
uv run python scripts/evolve_population.py \
  --generations 4 \
  --population-size 10 \
  --survivors 3 \
  --n-matches 70 \
  --n-games-per-match 10 \
  --objective ev \
  --out-dir research_logs/experiment_outputs
```

### Sync discovery to PocketBase

```bash
uv run python scripts/pocketbase/sync_discovery.py \
  --base-url http://<pocketbase-host>:8090 \
  --admin-token <token> \
  --commit "$(git rev-parse HEAD)"
```

## Notes for future rollouts

- During compaction, explicitly keep `research_logs/000_god_prompt.md` referenced as the high-level spec anchor.
- If day-of rules change, apply `research_logs/2026-03-01_day_of_patch_guide.md` first, then rerun quick champion recompute.

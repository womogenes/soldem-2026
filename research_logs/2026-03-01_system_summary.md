# Sold 'Em system summary

Local timestamp: 2026-03-01 03:51:12 PST

## What is ready now

- Verified rules/engine alignment and recomputed full hand rarity counts for the 50-card deck.
- Implemented parameterized strategy loading with spec strings (for example `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`).
- Added advanced strategy family:
- `prob_value`
- `risk_sniper`
- `seller_extraction`
- Ran evolutionary search and broad validation (objective, horizon, correlation, rule-profile variants).
- Integrated winning strategy as default champion in API/HUD flow.
- Added PocketBase sync tooling and improved AWS worker launch script for remote batch jobs.
- Provisioned and synced active PocketBase node for this rollout at `http://3.236.115.133:8090`.
- Added day-of rapid rule-variation patch runbook.
- Backend and web UI both pass smoke checks/build checks.

## Best current strategy

- Recommended objective-specific champions:
- `ev`: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
- `first_place`: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
- `robustness`: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
- Evidence path:
- Legacy high-confidence distributed runs favored `reserve_bid_floor=0.086`:
  - 777 / 864 scenario wins across runs `20260301-015615`, `20260301-020134`, `20260301-021037`, `20260301-023132`.
- Targeted EC2 param sweep (`20260301-024646`) found stronger `reserve_bid_floor=0.06` variants:
  - top candidate `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`
  - mean delta vs old champion: `+19.424` over 108 scenarios (95 wins, 13 losses).
- Fresh distributed EC2 validation (`20260301-030400`, 216 scenarios, `n_matches=180`) with expanded pool:
  - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`: 105 wins
  - `seller_extraction:opportunistic_delta=3600,reserve_bid_floor=0.06,sell_count=2`: 105 wins
  - old champion `reserve_bid_floor=0.086`: 4 wins
  - objective leaders:
    - `ev`: tie between 4000/3600 variants (34 each), session default set to 4000 variant
    - `first_place`: 4000 variant
    - `robustness`: 3600 variant
- Expanded-pool distributed EC2 run (`20260301-031824`, 216 scenarios, `n_matches=240`, 26 strategies) surfaced stronger candidates:
  - `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`: 90 scenario wins
  - `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`: 43 scenario wins
- Targeted EC2 param sweep confirmation (`20260301-033100`, champion fixed to 3300/0.029/2, 11 challengers):
  - no challenger achieved positive mean delta vs champion
  - best challenger `5400/0.032/2` still at mean delta `-1.475` (46 wins, 62 losses)
  - recommendation upgraded to `3300/0.029/2` for all objectives.
- 10-game-format extraction (`horizon=10`) from run `20260301-033100`:
  - artifact: `research_logs/experiment_outputs/horizon10_confirmation_20260301-033100.json`
  - confirms only marginal challenger edge slices; retained primary recommendation unchanged.

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
- `research_logs/experiment_outputs/distributed_20260301-021037/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-023132/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-022349/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-022736/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-030400/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-031824/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-015615.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-020134.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-021037.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-023132.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-022349.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-022736.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-030400.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-031824.json`
- `research_logs/experiment_outputs/distributed_master_summary_20260301.json`
- `research_logs/experiment_outputs/param_sweep_20260301-024646/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-030400.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-033100.json`
- `research_logs/experiment_outputs/evolution_20260301-025553/aggregate_summary.json`
- `research_logs/experiment_outputs/evolution_20260301-025732/aggregate_summary.json`
- `research_logs/experiment_outputs/param_sweep_20260301-033100/aggregate_summary.json`
- `research_logs/experiment_outputs/horizon10_confirmation_20260301-033100.json`

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

### Load champions from latest distributed artifact

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path": null}'
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

# Research runbook

Local timestamp: 2026-03-01 01:35 PST

Use this runbook for continued overnight strategy research.

## 1) Long replicated matrix

```bash
python scripts/run_long_parallel_matrix.py \
  --n-matches 320 \
  --replicates 5 \
  --workers 12 \
  --rule-profiles baseline_v1 standard_rankings seller_self_bid single_card_sell \
  --objectives ev first_place robustness \
  --horizons 10 \
  --corr-modes none respect herd kingmaker \
  --seed 5000 \
  --out-dir research_logs/experiment_outputs
```

Analyze output:

```bash
python scripts/analyze_long_matrix.py research_logs/experiment_outputs/long_parallel_matrix_<timestamp>.json
```

Build policy files from analysis:

```bash
python scripts/build_dayof_policy.py research_logs/experiment_outputs/long_parallel_matrix_<timestamp>.analysis.json \
  --winner-mode mean \
  --out research_logs/experiment_outputs/dayof_policy_<timestamp>_mean.json

python scripts/build_dayof_policy.py research_logs/experiment_outputs/long_parallel_matrix_<timestamp>.analysis.json \
  --winner-mode lcb \
  --out research_logs/experiment_outputs/dayof_policy_<timestamp>_lcb.json
```

## 2) Research-backed matrix (faster)

```bash
python scripts/run_research_backed_experiments.py --n-matches 60 --seed 900
```

## 3) Variant sweep for parameterized families

```bash
python scripts/run_research_variant_sweep.py --n-matches 100 --seed 1800
```

## 4) Evolutionary parameter search

```bash
python scripts/run_evolution_search.py \
  --generations 6 \
  --population 16 \
  --elite 6 \
  --n-matches 60 \
  --seed 8100
```

## 5) Correlation-strength stress sweep

```bash
python scripts/run_correlation_sweep.py \
  --n-matches 120 \
  --replicates 3 \
  --strengths 0.0 0.2 0.4 0.6 \
  --workers 12
```

## 6) Operational policy update loop

1. Run long matrix.
2. Analyze winner stability and margin.
3. Build policy maps from analysis and prefer `--winner-mode lcb` for day-of safety.
4. Promote stable winners into champion map.
5. Optional combine across analyses:
```bash
python scripts/build_combined_policy.py <analysis_a.json> <analysis_b.json> ... \
  --rule-profile baseline_v1 \
  --winner-mode lcb \
  --out research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_lcb.json
```

Build one global day-of map with profile coverage:

```bash
python scripts/merge_policy_maps.py \
  research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_lcb.json \
  research_logs/experiment_outputs/dayof_policy_combined_standard_rankings_v5_lcb.json \
  research_logs/experiment_outputs/dayof_policy_combined_seller_self_bid_v5_lcb.json \
  research_logs/experiment_outputs/dayof_policy_combined_single_card_sell_v5_lcb.json \
  --default-from research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_lcb.json \
  --out research_logs/experiment_outputs/dayof_policy_global_v7_lcb.json
```

Build human-opponent hybrid map (global coverage + hero-pool overrides):

```bash
python scripts/merge_policy_maps.py \
  research_logs/experiment_outputs/dayof_policy_global_v7_lcb.json \
  research_logs/experiment_outputs/hero_pool_policy_<timestamp_a>_lcb.json \
  research_logs/experiment_outputs/hero_pool_policy_<timestamp_b>_lcb.json \
  research_logs/experiment_outputs/hero_pool_policy_<timestamp_c>_lcb.json \
  research_logs/experiment_outputs/hero_pool_policy_<timestamp_d>_lcb.json \
  --default-from research_logs/experiment_outputs/dayof_policy_defaults_v9.json \
  --out research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json
```
6. Recompute backend champions:
```bash
curl -s -X POST http://127.0.0.1:8000/strategies/recompute_champions \
  -H 'content-type: application/json' \
  -d '{"n_matches":120,"n_games_per_match":10,"seed":42}'
```
7. Verify in HUD.

## 7) Logging discipline

- Append timestamps and actions to `research_logs/2026-03-01_live_log.md` after each major experiment.
- Keep all generated artifacts under `research_logs/experiment_outputs/`.

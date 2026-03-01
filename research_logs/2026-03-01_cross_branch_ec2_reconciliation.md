Local timestamp start: 2026-03-01 07:39 PST
Local timestamp end: 2026-03-01 08:00 PST

## Objective
Run cross-branch (`v2`/`v3`/`v4`/`v5`) tournament reconciliation on EC2 in under ~5 minutes per sweep, identify materially different strategy behavior, and produce day-of champion mapping.

## What was integrated before running
- Added mixed-strategy spec support in loader so both `tag|k=v` and `tag:k=v,...` are valid.
- Ensured branch-differentiated tags are available in `v2` runtime pool (including `market_maker_v2`, `regime_switch_v2`, `equity_evolved_v1`, `meta_switch_v4`, `prob_value`, `risk_sniper`, `seller_extraction`).
- Imported `v5` EC2 distributed scripts and extended launcher with `--scenario-preset fast|medium|full`.

## EC2 runs
- AWS account: `539881456097`
- Bucket: `soldem-2026-539881456097-1772358537`
- Artifact: `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_v2_cross_20260301-074128.tar.gz`
- Instance type used: `c7i.4xlarge`

1. Fast broad run
- Run ID: `20260301-074139`
- Workers: 18
- Preset: `fast` (2 profiles x 3 objectives x 1 horizon x 3 correlations = 18 scenarios)
- Strategies: 54 (all pooled tags + key parameterized variants)
- `n_matches`: 14
- Result summary: `research_logs/experiment_outputs/distributed_fast_20260301-074139_summary.json`
- Missing shards: 0

2. Medium broad run
- Run ID: `20260301-074335`
- Workers: 54
- Preset: `medium` (3 profiles x 3 objectives x 2 horizons x 3 correlations = 54 scenarios)
- Strategies: 54
- `n_matches`: 10
- Result summary: `research_logs/experiment_outputs/distributed_medium_20260301-074335_summary.json`
- Missing shards: 1 (worker 43; instance remained running and was terminated after collection)

3. Focused exploitability run
- Run ID: `20260301-074854`
- Workers: 18
- Preset: `fast` (18 scenarios)
- Strategies: top 16 contenders (`research_logs/cross_branch_focus_top16_20260301.txt`)
- `n_matches`: 60
- Result summary: `research_logs/experiment_outputs/distributed_focus_20260301-074854_summary.json`
- Missing shards: 0

## Summary of results

### Broad winner frequency (fast + medium, 71 scenario rows)
Top winners by scenario:
- `seller_extraction:opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2` -> 9
- `regime_switch_robust` -> 7
- `conservative_plus` -> 6
- `seller_extraction` -> 5
- `market_maker_tight` -> 4
- `seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2` -> 4

Interpretation: `v5`-style seller-extraction family is materially different from older pools and dominates broad winner counts.

### Focused run winner frequency (18 scenario rows)
- `seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2` -> 8
- `meta_switch_v4` -> 5
- `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2` -> 4
- `seller_extraction:opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2` -> 1

Interpretation: once the field is narrowed to strongest candidates and `n_matches` is raised, the 2600-variant extraction policy becomes the most stable winner.

### Exploitability reconciliation (focused top-16)
Pairwise dominance metric: fraction of scenario leaderboards where A's objective metric beats B's.

- `seller_extraction:...2600...`
  - Average pairwise win-rate vs field: 0.856
  - Worst-opponent win-rate: 0.611 (vs `seller_extraction:...3300...`)
  - Conclusion: least exploitable among tested contenders.

- `seller_extraction:...4500...`
  - Average pairwise win-rate vs field: 0.819
  - Worst-opponent win-rate: 0.333 (loses to `...2600...`)
  - Conclusion: high-upside but exploitable by tighter extraction variants.

- `meta_switch_v4`
  - Best first-place specialist in focused objective slices.
  - Negative pairwise margin vs leading extraction variants.
  - Conclusion: keep as objective-specific specialist, not default EV/robust policy.

- `regime_switch_robust`, `conservative_plus`
  - Broad wins in larger heterogeneous pool.
  - Strongly exploited in focused top-16 by extraction family.
  - Conclusion: fallback/backup policies, not primary champion.

## Day-of policy output
Generated policy file:
- `research_logs/experiment_outputs/dayof_policy_cross_branch_reconciled_v12.json`

Default mapping:
- `ev` -> `seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2`
- `first_place` -> `meta_switch_v4`
- `robustness` -> `seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2`

Alternates are included in the same file.

## API/HUD integration
`game/api.py` auto-load candidate list now prioritizes:
- `research_logs/experiment_outputs/dayof_policy_cross_branch_reconciled_v12.json`

This makes the reconciled policy load first on service startup (unless `SOLDEM_POLICY_PATH` is explicitly set).

## Cost control and cleanup
All instances for run IDs `20260301-074139`, `20260301-074335`, and `20260301-074854` were terminated after result collection.


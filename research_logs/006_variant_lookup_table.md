# Variant lookup table

Local time: 2026-03-01 02:48 PST

## Method

- Primary sources:
  - `research_logs/experiment_outputs/quick_variant_hero_suite_v3/`
  - `research_logs/experiment_outputs/evolved_variant_checks/`
- Candidates evaluated: `conservative_plus`, `equity_evolved_v1`, `equity_sniper_ultra`, `meta_switch`, `pot_fraction`.
- Correlation scenarios averaged: none, respect, herd, kingmaker.
- Table budget used in this pass: `n_tables=24`, `n_games=10`.

## Lookup table

1. baseline (`baseline_v1`)
- EV: `conservative_plus`
- first-place: `meta_switch`
- robustness: `equity_evolved_v1`

2. top2 split (`top2_split`)
- EV: `equity_evolved_v1`
- first-place: `equity_evolved_v1`
- robustness: `equity_evolved_v1`

3. high-low split (`high_low_split`)
- EV: `equity_evolved_v1`
- first-place: `equity_evolved_v1`
- robustness: `equity_evolved_v1`

4. seller self-bid (`seller_self_bid`)
- EV: `equity_evolved_v1`
- first-place: `equity_evolved_v1`
- robustness: `equity_evolved_v1`

5. weird short stack (`n_orbits=2,start_chips=120,ante_amt=25`)
- EV: `equity_evolved_v1`
- first-place: `meta_switch`
- robustness: `equity_evolved_v1`

## Practical policy for day-of

1. Safe default when uncertain:
- EV and robustness: `conservative_plus`
- first-place: `equity_evolved_v1`

2. If quick solver supports a specific variant and time allows manual lock:
- apply variant with `scripts/day_of_patch.py`
- lock with `--set-ev`, `--set-first-place`, `--set-robustness`

3. Use caution with `pot_fraction`:
- can top first-place in short-stack/passive regimes
- has much worse downside tails in broader mixed-field tests

## Regeneration command

`uv run python scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{}' --n-tables 24 --n-games 10 --out research_logs/experiment_outputs/quick_variant_hero_suite_v3/baseline.json`

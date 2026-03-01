# Variant lookup table

Local time: 2026-03-01 06:34 PST

## Method

- Primary sources:
  - `research_logs/experiment_outputs/night_qvhs_baseline_v1_50t_seed41001.json`
  - `research_logs/experiment_outputs/night_qvhs_top2_split_50t_seed41002.json`
  - `research_logs/experiment_outputs/night_qvhs_high_low_split_50t_seed41003.json`
  - `research_logs/experiment_outputs/night_qvhs_single_card_sell_50t_seed41004.json`
  - `research_logs/experiment_outputs/night_qvhs_seller_self_bid_50t_seed41005.json`
  - `research_logs/experiment_outputs/night_qvhs_standard_rankings_50t_seed41006.json`
  - `research_logs/experiment_outputs/night_qvhs_baseline_v1_first_place_150t_seed42001.json`
  - `research_logs/experiment_outputs/night_qvhs_seller_self_bid_first_place_150t_seed42002.json`
- Candidates evaluated: `conservative_plus`, `equity_evolved_v1`, `equity_sniper_ultra`, `meta_switch`, `pot_fraction`.
- Correlation scenarios averaged: none, respect, herd, kingmaker.
- Table budget used in this pass:
  - broad sweep: `n_tables=50`, `n_games=10`
  - first-place tie-break: `n_tables=150`, `n_games=10` on baseline/seller-self-bid

## Lookup table

1. baseline (`baseline_v1`)
- EV: `equity_evolved_v1`
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

5. single-card sell (`single_card_sell`)
- EV: `equity_evolved_v1`
- first-place: `equity_evolved_v1`
- robustness: `equity_evolved_v1`

6. standard rankings (`standard_rankings`)
- EV: `equity_evolved_v1`
- first-place: `equity_evolved_v1`
- robustness: `equity_evolved_v1`

7. weird mixed overrides (stress sample)
- EV: `equity_evolved_v1`
- robustness: `equity_evolved_v1`
- first-place:
  - sprint-like short-stack (`n_orbits<=2` and `start_chips<=150`) with `winner_takes_all`: `pot_fraction`
  - winner-takes-all pot-pressure (`n_orbits>=3` and (`ante_amt/start_chips>=0.25` or `ante_amt>=50`)): `pot_fraction`
  - winner-takes-all high-stack low-ante (`n_orbits>=3`, `start_chips>=180`, `ante/start<0.20`): `equity_evolved_v1`
  - remaining non-sprint winner-takes-all band: `meta_switch`
  - otherwise: `equity_evolved_v1`

## Practical policy for day-of

1. Safe default when uncertain:
- EV and robustness: `equity_evolved_v1`
- first-place:
  - exact baseline: `meta_switch`
  - sprint short-stack (`n_orbits<=2`, low stack) only when `winner_takes_all`: `pot_fraction`
  - winner-takes-all pot-pressure (`n_orbits>=3` and (`ante/start>=0.25` or `ante>=50`)): `pot_fraction`
  - winner-takes-all high-stack low-ante (`n_orbits>=3`, `start>=180`, `ante/start<0.20`): `equity_evolved_v1`
  - remaining non-sprint winner-takes-all band: `meta_switch`
  - otherwise: `equity_evolved_v1`

2. If quick solver supports a specific variant and time allows manual lock:
- apply variant with `scripts/day_of_patch.py`
- lock with `--set-ev`, `--set-first-place`, `--set-robustness`

3. Use caution with `pot_fraction`:
- can top first-place in short-stack/passive regimes
- has much worse downside tails in broader mixed-field tests

## Regeneration command

`uv run python scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --n-tables 50 --n-games 10 --out research_logs/experiment_outputs/night_qvhs_baseline_v1_50t_seed41001.json`

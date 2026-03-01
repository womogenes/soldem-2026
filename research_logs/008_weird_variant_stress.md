# Weird variant stress summary

Local time: 2026-03-01 03:59 PST

## Scope

- Objective: stress unknown rule mixes for short-horizon play (`n_games=10`).
- Method: `scripts/quick_variant_hero_solver.py` with `n_tables=40` per variant, averaged across correlation scenarios.
- Candidates: `conservative_plus`, `equity_evolved_v1`, `equity_sniper_ultra`, `meta_switch`, `pot_fraction`, `house_hammer`.

## Variants tested

1. short stack sprint
- overrides: `{"start_chips":120,"ante_amt":25,"n_orbits":2}`
- artifact: `research_logs/experiment_outputs/night_weird_shortstack_mix_40t_seed51001.json`

2. deep stack long horizon
- overrides: `{"start_chips":300,"ante_amt":40,"n_orbits":5}`
- artifact: `research_logs/experiment_outputs/night_weird_deepstack_mix_40t_seed51002.json`

3. self-bid plus top2 split
- overrides: `{"seller_can_bid_own_card":true,"pot_distribution_policy":"top2_split"}`
- artifact: `research_logs/experiment_outputs/night_weird_selfbid_top2_40t_seed51003.json`

4. standard ranking plus high-low plus single-card
- overrides: `{"hand_ranking_policy":"standard_plus_five_kind","pot_distribution_policy":"high_low_split","allow_multi_card_sell":false}`
- artifact: `research_logs/experiment_outputs/night_weird_std_highlow_single_40t_seed51004.json`

5. short stack plus self-bid
- overrides: `{"start_chips":140,"ante_amt":30,"n_orbits":2,"seller_can_bid_own_card":true}`
- artifact: `research_logs/experiment_outputs/night_weird_short_selfbid_40t_seed51005.json`

## Results

- EV winners: `equity_evolved_v1` in 5/5.
- Robustness winners: `equity_evolved_v1` in 5/5.
- First-place winners:
  - `equity_evolved_v1` in 3/5.
  - `pot_fraction` in 2/5 (both sprint-like short-stack variants).

## Day-of rule

1. If objective is `ev` or `robustness`, use `equity_evolved_v1`.
2. If objective is `first_place` and rule shape is sprint (`n_orbits<=2` and `start_chips<=150`), use `pot_fraction`.
3. Otherwise for `first_place`, use:
- baseline profile: `meta_switch`
- non-baseline variants: `equity_evolved_v1`

## Reproduction commands

```bash
uv run scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"start_chips":120,"ante_amt":25,"n_orbits":2}' --n-tables 40 --n-games 10 --seed 51001 --out research_logs/experiment_outputs/night_weird_shortstack_mix_40t_seed51001.json
uv run scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"start_chips":300,"ante_amt":40,"n_orbits":5}' --n-tables 40 --n-games 10 --seed 51002 --out research_logs/experiment_outputs/night_weird_deepstack_mix_40t_seed51002.json
uv run scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"seller_can_bid_own_card":true,"pot_distribution_policy":"top2_split"}' --n-tables 40 --n-games 10 --seed 51003 --out research_logs/experiment_outputs/night_weird_selfbid_top2_40t_seed51003.json
uv run scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"hand_ranking_policy":"standard_plus_five_kind","pot_distribution_policy":"high_low_split","allow_multi_card_sell":false}' --n-tables 40 --n-games 10 --seed 51004 --out research_logs/experiment_outputs/night_weird_std_highlow_single_40t_seed51004.json
uv run scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"start_chips":140,"ante_amt":30,"n_orbits":2,"seller_can_bid_own_card":true}' --n-tables 40 --n-games 10 --seed 51005 --out research_logs/experiment_outputs/night_weird_short_selfbid_40t_seed51005.json
```

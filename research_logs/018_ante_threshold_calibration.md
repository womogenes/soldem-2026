# Ante threshold calibration

Local time: 2026-03-01 05:29 PST

## Goal

Recalibrate the first-place high-ante `pot_fraction` trigger with direct sweeps around the previous cutoff.

## Experiments

1. Broad grid sweep (`19` cases x `2` seeds, first-place only)
- Command:
  - `uv run python scripts/ante_threshold_sweep.py --n-tables 6 --n-games 8 --seeds 62001,62002 --out research_logs/experiment_outputs/ante_threshold_sweep_19c_2s_6t8g_seed62001.json`
- Artifact:
  - `research_logs/experiment_outputs/ante_threshold_sweep_19c_2s_6t8g_seed62001.json`
- Signal:
  - non-sprint winner-takes-all at ratios `0.286+` consistently favored `pot_fraction` in this pass.
  - ratio `0.25` was mixed by profile (`meta_switch` and `pot_fraction` both appeared).

2. Near-threshold probe (`6` cases x `2` seeds)
- Artifact:
  - `research_logs/experiment_outputs/ante_threshold_probe_6c_2s_10t8g_seed62101.json`
- Signal:
  - at ratios `0.269` to `0.290`, all probed non-sprint winner-takes-all cases favored `pot_fraction`.

3. Focused ratio-0.25 confirmations (higher budget)
- Artifact:
  - `research_logs/experiment_outputs/ante_ratio_025_confirm_3c_2s_20t10g_seed62251.json`
- Signal:
  - `140/35/o4`: `meta_switch` both seeds (small gaps).
  - `160/40/o3`: split (`meta_switch` / `pot_fraction`).
  - `200/50/o4`: `pot_fraction` both seeds.

## Policy update

High-ante-pressure first-place trigger is now:

- `winner_takes_all`
- `n_orbits >= 3`
- and either:
  - `ante_amt / start_chips >= 0.27`, or
  - `ante_amt >= 50`

Sprint trigger remains unchanged:

- `n_orbits <= 2` and `start_chips <= 150` and `winner_takes_all` => `pot_fraction`.

## Why this rule

- It captures stable non-sprint winner-takes-all pockets found in the new sweeps (`~0.27+` ratio and absolute ante pressure cases like `200/50`).
- It avoids forcing `pot_fraction` for lower-pressure non-sprint cases like `140/35` where `meta_switch` repeatedly held a small edge.

## Implementation updates

- `game/api.py`
- `scripts/day_of_autosolve_patch.py`
- `tests/test_api_session.py`

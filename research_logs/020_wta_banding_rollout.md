# Winner-takes-all banding rollout

Local time: 2026-03-01 06:34 PST

## Why this was added

Earlier first-place routing forced many non-baseline variants to `equity_evolved_v1`. New near day-of rollouts (8-12 game horizons, correlated scenarios) showed this left first-place equity on the table in winner-takes-all variants.

## What changed

`first_place` routing now uses winner-takes-all banding after passive/sprint/baseline checks:

1. `pot_fraction` for winner-takes-all pot pressure (`n_orbits>=3` and (`ante/start>=0.25` or `ante>=50`)).
2. `equity_evolved_v1` for winner-takes-all high-stack low-ante relief (`n_orbits>=3`, `start>=180`, `ante/start<0.20`).
3. `meta_switch` for the remaining non-sprint winner-takes-all band.
4. `equity_evolved_v1` for non-winner-takes-all variants.

## Core evidence artifacts

- Matrix sweeps:
  - `research_logs/experiment_outputs/first_place_rollout_matrix_6c_3h_60m_seed63201.json`
- Hero confirmations:
  - `research_logs/experiment_outputs/hero_first_place_baseline_9s_80t10g_seed63401.json`
  - `research_logs/experiment_outputs/hero_first_place_low_ante_wta_9s_80t10g_seed63451.json`
  - `research_logs/experiment_outputs/hero_first_place_high_ante_ratio_9s_80t10g_seed63501.json`
  - `research_logs/experiment_outputs/hero_first_place_wta_o4_s200_a35_9s_80t10g_seed64001.json`
  - `research_logs/experiment_outputs/hero_first_place_wta_o4_s200_a45_9s_80t10g_seed64051.json`
- Policy evaluator:
  - `research_logs/experiment_outputs/first_place_policy_eval_post_wta_banding.json`

## Implementation files

- `game/api.py`
- `scripts/day_of_autosolve_patch.py`
- `scripts/policy_smoke.py`
- `scripts/evaluate_first_place_policy.py`
- `tests/test_api_session.py`
- `web/src/routes/+page.svelte`

## Validation status

- Backend tests: `32/32` passing.
- Web check/build: passing.
- Policy smoke: passing (including WTA pot-pressure, WTA high-stack relief, and 6-player branch checks).
- Integrated preflight (`tests + web + policy smoke`) passed at `2026-03-01 06:33 PST`.

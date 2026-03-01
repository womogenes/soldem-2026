# Ante threshold calibration

Local time: 2026-03-01 06:34 PST

## Goal

Refit first-place winner-takes-all routing for near day-of horizons (8-12 games) under correlation models, using both population and hero-vs-pool rollouts.

## New experiments

1. First-place rollout matrix (`6` rule cases x `3` horizons x `4` correlation scenarios)
- Script:
  - `scripts/first_place_rollout_matrix.py`
- Artifacts:
  - `research_logs/experiment_outputs/first_place_rollout_matrix_smoke_seed63101.json`
  - `research_logs/experiment_outputs/first_place_rollout_matrix_6c_3h_60m_seed63201.json`

2. Targeted first-place confirmations (population and hero-vs-pool)
- Baseline and low-ante WTA confirms:
  - `baseline_first_place_confirm_6s_140m_10g_seed63301.json`
  - `low_ante_wta_first_place_confirm_6s_140m_10g_seed63351.json`
- Hero-vs-pool anchor checks:
  - `hero_first_place_baseline_9s_80t10g_seed63401.json`
  - `hero_first_place_low_ante_wta_9s_80t10g_seed63451.json`
  - `hero_first_place_high_ante_ratio_9s_80t10g_seed63501.json`

3. Boundary probes for non-sprint winner-takes-all
- Mid-stack and high-stack checks:
  - `hero_first_place_wta_o4_s150_a35_9s_80t10g_seed63551.json`
  - `hero_first_place_wta_o4_s160_a35_9s_80t10g_seed63601.json`
  - `hero_first_place_wta_o4_s180_a35_9s_80t10g_seed63651.json`
  - `hero_first_place_wta_o4_s140_a30_9s_80t10g_seed63701.json`
  - `hero_first_place_wta_o4_s140_a40_9s_80t10g_seed63751.json`
  - `hero_first_place_wta_o4_s200_a35_9s_80t10g_seed64001.json`
  - `hero_first_place_wta_o4_s200_a45_9s_80t10g_seed64051.json`
- Ambiguous spot seed ensemble (`s=140, a=35, o=4`):
  - `hero_first_place_wta_o4_s140_a35_9s_80t10g_seed63801.json`
  - `hero_first_place_wta_o4_s140_a35_9s_80t10g_seed63851.json`
  - `hero_first_place_wta_o4_s140_a35_9s_80t10g_seed63901.json`
  - `hero_first_place_wta_o4_s140_a35_9s_80t10g_seed63951.json`

4. Policy evaluator refresh
- Script:
  - `scripts/evaluate_first_place_policy.py`
- Artifact:
  - `research_logs/experiment_outputs/first_place_policy_eval_post_wta_banding.json`
- Best fit on current artifact set:
  - ratio threshold `0.25` (`68/80`, hit rate `0.850`).

## Routing update

First-place resolver now uses winner-takes-all banding (after baseline/sprint/passive overrides):

- `pot_fraction` when:
  - sprint winner-takes-all (`n_orbits<=2` and `start_chips<=150`), or
  - winner-takes-all pot pressure (`n_orbits>=3` and (`ante/start>=0.25` or `ante>=50`)).
- `equity_evolved_v1` when:
  - winner-takes-all high-stack low-ante (`n_orbits>=3`, `start>=180`, `ante/start<0.20`).
- `meta_switch` when:
  - remaining non-sprint winner-takes-all band.
- Exact baseline still defaults to `meta_switch`.
- Non-winner-takes-all variants default to `equity_evolved_v1`.

## Why this rule

- It removes a weak prior where most non-baseline variants were forced to `equity_evolved_v1` for first-place.
- It preserves baseline behavior while adding empirically supported winner-takes-all banding for common day-of variant pockets.
- It improved offline artifact-policy alignment from `0.709` (current pre-change logic on latest set) to `0.848`.

## Implementation updates

- `game/api.py`
- `scripts/day_of_autosolve_patch.py`
- `scripts/policy_smoke.py`
- `scripts/evaluate_first_place_policy.py`
- `tests/test_api_session.py`
- `web/src/routes/+page.svelte`

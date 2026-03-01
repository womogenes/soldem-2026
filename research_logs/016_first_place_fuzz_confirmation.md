# First-place fuzz confirmation

Local time: 2026-03-01 05:09 PST

## Goal

Validate random-fuzz first-place outliers before changing day-of resolver policy.

## Stage 1: low-budget broad sweep

- Command:
  - `uv run python scripts/random_variant_fuzz.py --n-variants 16 --n-tables 4 --n-games 4 --seed 60111 --out research_logs/experiment_outputs/random_variant_fuzz_16v_seed60111_lowbudget.json`
- Artifact:
  - `research_logs/experiment_outputs/random_variant_fuzz_16v_seed60111_lowbudget.json`
- Winner counts (low-budget, noisy):
  - first-place: `equity_evolved_v1` 11/16, `equity_sniper_ultra` 2/16, `conservative_plus` 2/16, `pot_fraction` 1/16.

## Stage 2: medium-budget seeded confirmations

- Outlier variants rechecked (indexes from stage 1): `0, 5, 10, 12, 15`.
- Command pattern used:
  - `uv run python scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '<variant overrides>' --objectives first_place --n-tables 10 --n-games 8 --seed <seed> --out research_logs/experiment_outputs/random_variant_confirm2_first_<idx>_seed<seed>.json`
- Seeds used: `61001`, `61002`.
- Artifacts:
  - `research_logs/experiment_outputs/random_variant_confirm2_first_0_seed61001.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_0_seed61002.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_5_seed61001.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_5_seed61002.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_10_seed61001.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_10_seed61002.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_12_seed61001.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_12_seed61002.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_15_seed61001.json`
  - `research_logs/experiment_outputs/random_variant_confirm2_first_15_seed61002.json`

## Confirmed findings

- Variant `10` (`start_chips=140`, `ante_amt=50`, `n_orbits=4`, `winner_takes_all`) favored `pot_fraction` in both seeds with strong gaps.
- Sprint-like split-pot variants were unstable:
  - top2/high-low sprint outliers alternated between `equity_evolved_v1`, `conservative_plus`, and one `house_hammer` win.
  - no consistent evidence that sprint alone implies `pot_fraction` when pot is split.

## Policy update applied

- Keep exact baseline first-place default: `meta_switch`.
- Keep non-baseline first-place default: `equity_evolved_v1`.
- Keep passive high-confidence table-read override: `pot_fraction`.
- Refine sprint override:
  - use `pot_fraction` only when `n_orbits<=2`, `start_chips<=150`, and pot policy is `winner_takes_all`.
- Add high-ante-pressure override:
  - use `pot_fraction` when `ante_amt/start_chips>=0.33`, `n_orbits>=3`, and pot policy is `winner_takes_all`.

## Note

- A single aborted high-budget run was discarded and not used for final policy decisions.

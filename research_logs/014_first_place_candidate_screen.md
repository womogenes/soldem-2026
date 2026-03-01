# First-place candidate screen

Local time: 2026-03-01 04:40 PST

## Goal

Test whether a newly evolved first-place candidate can beat current baseline choices (`meta_switch`, `equity_evolved_v1`) strongly enough to promote.

## Candidate generation

- Script: `scripts/evolve_equity_family.py`
- Objective: `first_place`
- Run:
  - `--candidates 36 --n-tables 24 --n-games 10 --seed 58001`
- Top candidate found:
  - `equity_auto_034`
  - params (from output): `bid_multiplier=0.694`, `delta_scale=5454.5`, `min_delta=317`, `max_stack_frac=0.228`, `max_pot_frac=0.114`, `house_multiplier=1.359`, `preserve_weight=1.251`, `sell_count_early=2`, `sell_count_late=1`
- Artifact:
  - `research_logs/experiment_outputs/evolve_first_place_58001.json`

## Validation

- Benchmarked candidate against `meta_switch`, `equity_evolved_v1`, `pot_fraction`, `conservative_plus` under baseline first-place objective.
- Artifacts:
  - `research_logs/experiment_outputs/night_first_candidate_baseline_none_seed59010.json`
  - `research_logs/experiment_outputs/night_first_candidate_baseline_none_seed59012.json`
  - `research_logs/experiment_outputs/night_first_candidate_baseline_none_seed59013.json`
  - `research_logs/experiment_outputs/night_first_candidate_baseline_respect35_seed59011.json`
  - `research_logs/experiment_outputs/night_first_candidate_baseline_respect35_seed59014.json`
  - `research_logs/experiment_outputs/night_first_candidate_baseline_respect35_seed59015.json`

## Aggregate result

- none correlation (3 seeds):
  - first-place mean:
    - `equity_evolved_v1`: `0.428`
    - `meta_switch`: `0.394`
    - candidate: `0.387`
- respect 0.35 correlation (3 seeds):
  - first-place mean:
    - `equity_evolved_v1`: `0.418`
    - `meta_switch`: `0.403`
    - candidate: `0.370`

## Decision

- Candidate did not clear promotion bar against incumbents.
- Keep current policy:
  - baseline first-place: `meta_switch`
  - EV/robustness: `equity_evolved_v1`
  - sprint/passive first-place override: `pot_fraction`

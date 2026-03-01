# Research-backed strategy playbook

Local timestamp: 2026-03-01 01:28 PST

This playbook links peer-reviewed findings to concrete Sold 'Em strategy families and measured outcomes in this repository.

## Primary sources and operational translations

### Level-k and cognitive hierarchy bidding

Sources:

- Crawford and Iriberri (2007), *Econometrica*: https://econpapers.repec.org/RePEc:ecm:emetrp:v:75:y:2007:i:6:p:1721-1770
- Camerer, Ho, Chong (2004), *QJE*: https://academic.oup.com/qje/article-abstract/119/3/861/1938841
- Crawford, Costa-Gomes, Iriberri (2013), *JEL survey*: https://ideas.repec.org/a/aea/jeclit/v51y2013i1p5-62.html

Translation:

- Human bidders are heterogeneous in reasoning depth, not equilibrium homogeneous.
- Implemented `level_k`, `level_k_l1`, and `level_k_l3` with explicit depth assumptions and response-to-profile adaptation.

### Quantal response behavior (bounded rationality / noisy best response)

Source:

- McKelvey and Palfrey (1995), *Games and Economic Behavior*: https://www.sciencedirect.com/science/article/pii/S0899825685800272

Translation:

- Humans respond probabilistically to utility differences, not deterministically.
- Implemented `quantal_response`, `quantal_cold`, and `quantal_hot` to model temperature-scaled noisy utility choice over bid grids.

### Reciprocity in repeated first-price auctions

Sources:

- Amore et al. (2025 preprint), reciprocity in first-price auctions: https://arxiv.org/abs/2508.18512

Translation:

- Repeated interactions can create reciprocal concessions or punishments.
- Implemented `reciprocity_probe` to adjust bid intensity by seller extraction profile.

### Experience-weighted attraction learning

Sources:

- Camerer and Ho (1998), *Econometrica submission draft/chapter context on EWA*: https://authors.library.caltech.edu/records/4fh4n-4c340
- Erev and Roth (1998), *AER*: https://econpapers.repec.org/RePEc:aea:aecrev:v:88:y:1998:i:4:p:848-81

Translation:

- Repeated play against humans is better modeled by adaptive learning dynamics than static equilibrium.
- Implemented `ewa_attraction`, `ewa_slow`, and `ewa_fast` as attraction-updating bid policies.

### Safe exploitation under imperfect information

Source:

- Brown and Sandholm (2017), *NeurIPS*: https://papers.nips.cc/paper/6671-safe-and-nested-subgame-solving-for-imperfect-information-games

Translation:

- Pure exploitation can increase downside; safe constraints protect against counter-exploitation.
- Implemented `safe_exploit`, `safe_exploit_robust`, `safe_exploit_aggro` as blended conservative/exploit policies.

### Winner’s curse mitigation in common-value uncertainty

Sources:

- Kagel and Levin (1986): https://econpapers.repec.org/RePEc:aea:aecrev:v:76:y:1986:i:5:p:894-920

Translation:

- Aggressive winning can be value-destructive when uncertainty is high.
- Implemented `winners_curse_aware` with uncertainty- and aggression-aware bid shading.

### Multiplayer practical adaptation and local re-solving

Sources:

- DeepStack (2017): https://pubmed.ncbi.nlm.nih.gov/28254783/
- Pluribus (2019): https://pubmed.ncbi.nlm.nih.gov/31296650/

Translation:

- Use robust baseline + local adaptation from observed opponents.
- Current default operationally remains conservative baseline with profile-aware challengers.

## Experiment outputs generated in this pass

### Full objective-horizon-correlation matrix

- JSON: [research_backed_matrix_20260301_012345.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/research_backed_matrix_20260301_012345.json)
- Summary: [research_backed_matrix_20260301_012345.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/research_backed_matrix_20260301_012345.md)

Result highlights:

- `conservative` won 27/27 scenarios across objectives (`ev`, `first_place`, `robustness`), horizons (5/10/20), and correlation modes (`none`, `respect`, `herd`).
- Best research-derived challenger by average performance was `level_k`.

### Variant parameter sweep

- JSON: [research_variant_sweep_20260301_012452.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/research_variant_sweep_20260301_012452.json)
- Summary: [research_variant_sweep_20260301_012452.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/research_variant_sweep_20260301_012452.md)

Aggregate top by expected PnL:

1. `conservative`
2. `level_k`
3. `pot_fraction`
4. `level_k_l3`

`quantal_*`, `ewa_*`, and `safe_exploit_*` underperform with current calibration and should remain exploration candidates, not defaults.

### Long replicated matrix with rule/correlation stress testing

- Matrix (multi-profile): [long_parallel_matrix_20260301_012847.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/long_parallel_matrix_20260301_012847.md)
- Matrix (baseline high-sample incl. newer tags): [long_parallel_matrix_20260301_013735.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/long_parallel_matrix_20260301_013735.md)
- Matrix (extended high-sample h10 stress): [long_parallel_matrix_20260301_020705.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/long_parallel_matrix_20260301_020705.md)

Result highlights:

- `conservative` remains highest average EV and highest champion count.
- `meta_switch_soft` is a strong second policy and wins many correlation/robustness pockets.
- `meta_switch` remains a meaningful fallback for correlated/kingmaker-like dynamics.
- `winners_curse_aware` and `reciprocity_probe` did not hold up in high-sample baseline tests and are not day-of defaults.
- In the extended h10 stress analysis (`winner_counts`: `conservative=31`, `meta_switch=9`, `meta_switch_soft=8`), both mean and LCB policy defaults stayed `conservative` for baseline objective defaults.

### Evolutionary parameter tuning and validation bracket

- Evolution search output: [evolution_search_20260301_015202.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/evolution_search_20260301_015202.md)
- Head-to-head validation output: [evolved_head_to_head_20260301_0200.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/evolved_head_to_head_20260301_0200.json)

Result highlights:

- Evolution converged to tuned `level_k` variants (especially `level=2/3` with moderate `l0_fraction` values).
- In focused h10 baseline brackets, tuned `level_k` variants won most EV/robustness scenarios, while `meta_switch_soft` retained strength in kingmaker and some first-place pockets.
- A deployable evolved policy map is available:
  - [dayof_policy_evolved_h10.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/dayof_policy_evolved_h10.json)

### Focused evolved candidate validation and full-field cross-check

- Focused evolved pool run (baseline h10 reduced candidate set, including tuned `level_k` specs):
  - [long_parallel_matrix_20260301_023315.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/long_parallel_matrix_20260301_023315.md)
- Full-field cross-check with evolved specs inserted into broad strategy population:
  - [long_parallel_matrix_20260301_024017.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/long_parallel_matrix_20260301_024017.md)

Result highlights:

- In reduced-candidate tests, tuned `level_k` variants dominated.
- In full-field tests, evolved `level_k` variants won specific pockets, but aggregate EV leaders remained `meta_switch_soft` and `conservative`.
- Integrated combined defaults after adding longer multi-horizon and multi-profile runs:
  - [dayof_policy_combined_baseline_v7_mean.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_mean.json)
  - [dayof_policy_combined_baseline_v7_lcb.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_lcb.json)
  - [dayof_policy_global_v7_lcb.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/dayof_policy_global_v7_lcb.json)
  - Default summary: `ev=meta_switch_soft`, `first_place=conservative`, `robustness=conservative`.

### Correlation-strength sweep (social dynamics stress)

- Output: [correlation_sweep_20260301_025118.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/correlation_sweep_20260301_025118.md)

Result highlights:

- In focused candidate tests, increasing correlation strength shifted winners toward tuned `level_k` variants.
- `level_k_l3` and `level_k|level=2|l0_fraction=0.309|tag=levelk_207605` were strongest in many high-correlation robustness scenarios.
- Day-of implication: keep conservative baseline defaults, but prepare evolved `level_k` overrides if live table dynamics become explicitly reciprocal/kingmaker-like.

### Hero-vs-human-pool matrix (day-of realism)

- Outputs:
  - [hero_pool_matrix_20260301_054854.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/hero_pool_matrix_20260301_054854.md)
  - [hero_pool_policy_20260301_054854_lcb.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/hero_pool_policy_20260301_054854_lcb.json)
  - [hero_pool_matrix_20260301_061711.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/hero_pool_matrix_20260301_061711.md)
  - [hero_pool_matrix_20260301_064413.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/hero_pool_matrix_20260301_064413.md)
  - [hero_pool_matrix_20260301_065716.md](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/hero_pool_matrix_20260301_065716.md)

Result highlights:

- Under weighted human-like opponent pools, baseline defaults shifted relative to pure round-robin:
  - `ev` stayed `meta_switch_soft`
  - high-sample h10 validation favored `first_place=conservative`
  - high-sample h10 validation favored `robustness=level_k`
- Final focused `standard_rankings` first-place rerun confirmed `conservative` in all four correlation modes (including kingmaker), removing the prior low-margin ambiguity.
- Promoted hybrid policy (global profile coverage + hero overrides):
  - [dayof_policy_hybrid_v11_lcb.json](/home/willi/coding/trading/soldem-2026/v2/research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json)

## Research-backed deployment guidance (current)

- Default champion: `conservative`
- Secondary challenger: `meta_switch_soft` (with `meta_switch` close behind in some conditions)
- High-variance fallback for passive tables: `pot_fraction`
- Keep `quantal_*`, `ewa_*`, `winners_curse_aware`, and `reciprocity_probe` for additional calibration passes with real human logs.

## What informs future exploration going forward

All future strategy exploration should now be grounded in these source-anchored hypotheses and tracked by tag:

- CH/level-k family: `level_k*`
- QRE family: `quantal_*`
- EWA family: `ewa_*`
- Safe exploitation family: `safe_exploit_*`
- Reciprocity family: `reciprocity_probe`
- Winner's-curse mitigation family: `winners_curse_aware`
- Robust baseline family: `conservative`
- Policy-switching family: `meta_switch*`

Use `scripts/run_research_backed_experiments.py` and `scripts/run_research_variant_sweep.py` as default entry points for further search.

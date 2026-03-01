# Day-of strategy matrix (from long replicated runs)

Local timestamp: 2026-03-01 01:40 PST

Sources:

- `research_logs/experiment_outputs/long_parallel_matrix_20260301_012847.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_013735.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_020705.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_024017.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_025448.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_030443.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_033913.analysis.json`
- `research_logs/experiment_outputs/long_parallel_matrix_20260301_040636.analysis.json`
- `research_logs/experiment_outputs/hero_pool_matrix_20260301_054854.json`
- `research_logs/experiment_outputs/hero_pool_matrix_20260301_061711.json`
- `research_logs/experiment_outputs/hero_pool_matrix_20260301_064413.json`
- `research_logs/experiment_outputs/hero_pool_matrix_20260301_065716.json`
- combined policy files:
  - `research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_mean.json`
  - `research_logs/experiment_outputs/dayof_policy_combined_baseline_v7_lcb.json`
  - `research_logs/experiment_outputs/dayof_policy_global_v7_lcb.json`
  - `research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json`

## Recommended baseline default

- Combined-policy defaults from both long replicated runs:
  - `ev`: `meta_switch_soft` (LCB policy) / `meta_switch_soft` (mean policy v7)
  - `first_place`: `conservative`
  - `robustness`: `conservative` (LCB policy) / `conservative` (mean policy v7)
- Use condition-specific overrides below when evidence supports them (especially in correlated/kingmaker tables).

## Human-pool hybrid default

- Hybrid policy (`global_v7` + hero-pool overrides) default:
  - `ev`: `meta_switch_soft`
  - `first_place`: `conservative`
  - `robustness`: `level_k`
- File: `research_logs/experiment_outputs/dayof_policy_hybrid_v11_lcb.json`
- This is intended for day-of play against humans while preserving non-baseline condition coverage from global policy maps.
- Final focused `standard_rankings` first-place rerun (`hero_pool_matrix_20260301_065716`) removed the prior kingmaker ambiguity and now selects `conservative` across all four correlation modes by both mean and LCB.

## Condition overrides with non-conservative winner

- `baseline_v1 | ev | h5 | kingmaker` -> `meta_switch` (margin `0.9644` over `conservative`)
- `baseline_v1 | ev | h5 | none` -> `meta_switch` (margin `16.9059` over `meta_switch_soft`)
- `baseline_v1 | ev | h10 | respect` -> `meta_switch_soft` (margin `10.3061` over `conservative`)
- `baseline_v1 | ev | h20 | kingmaker` -> `meta_switch_soft` (margin `37.2539` over `level_k_l3`)
- `baseline_v1 | ev | h20 | respect` -> `meta_switch_soft` (margin `8.7825` over `conservative`)
- `baseline_v1 | first_place | h5 | herd` -> `meta_switch_soft` (margin `0.0335` over `conservative`)
- `baseline_v1 | first_place | h5 | kingmaker` -> `meta_switch_soft` (margin `0.0774` over `pot_fraction`)
- `baseline_v1 | first_place | h10 | herd` -> `meta_switch_soft` (margin `0.0301` over `pot_fraction`)
- `baseline_v1 | first_place | h10 | kingmaker` -> `meta_switch_soft` (margin `0.0219` over `conservative`)
- `baseline_v1 | first_place | h10 | respect` -> `meta_switch_soft` (margin `0.1205` over `meta_switch`)
- `baseline_v1 | first_place | h20 | herd` -> `meta_switch_soft` (margin `0.0058` over `pot_fraction`)
- `baseline_v1 | first_place | h20 | kingmaker` -> `meta_switch_soft` (margin `0.0011` over `level_k`)
- `baseline_v1 | first_place | h20 | none` -> `meta_switch_soft` (margin `0.0131` over `meta_switch`)
- `baseline_v1 | first_place | h20 | respect` -> `meta_switch_soft` (margin `0.0516` over `conservative`)
- `baseline_v1 | robustness | h5 | herd` -> `meta_switch` (margin `29.9838` over `conservative`)
- `baseline_v1 | robustness | h5 | kingmaker` -> `meta_switch` (margin `2.3944` over `level_k_l3`)
- `baseline_v1 | robustness | h5 | respect` -> `meta_switch` (margin `36.7318` over `level_k_l3`)
- `baseline_v1 | robustness | h10 | herd` -> `meta_switch` (margin `24.7492` over `meta_switch_soft`)
- `baseline_v1 | robustness | h10 | respect` -> `meta_switch` (margin `5.7881` over `conservative`)
- `baseline_v1 | robustness | h20 | kingmaker` -> `meta_switch` (margin `22.0530` over `level_k_l3`)
- `baseline_v1 | robustness | h20 | none` -> `meta_switch` (margin `1.3905` over `meta_switch_soft`)
- `baseline_v1 | robustness | h20 | respect` -> `meta_switch` (margin `5.6745` over `meta_switch_soft`)
- `seller_self_bid | ev | h5 | herd` -> `meta_switch_soft` (margin `13.9870` over `pot_fraction`)
- `seller_self_bid | ev | h10 | kingmaker` -> `meta_switch_soft` (margin `9.1133` over `conservative`)
- `seller_self_bid | ev | h20 | kingmaker` -> `meta_switch` (margin `12.2567` over `conservative`)
- `seller_self_bid | ev | h20 | respect` -> `meta_switch_soft` (margin `46.7887` over `pot_fraction`)
- `seller_self_bid | first_place | h5 | herd` -> `pot_fraction` (margin `0.0061` over `conservative`)
- `seller_self_bid | first_place | h5 | kingmaker` -> `meta_switch_soft` (margin `0.0036` over `conservative`)
- `seller_self_bid | first_place | h10 | herd` -> `pot_fraction` (margin `0.0703` over `seller_profit`)
- `seller_self_bid | first_place | h10 | kingmaker` -> `pot_fraction` (margin `0.0139` over `conservative`)
- `seller_self_bid | first_place | h10 | none` -> `meta_switch_soft` (margin `0.0012` over `conservative`)
- `seller_self_bid | first_place | h20 | herd` -> `pot_fraction` (margin `0.0087` over `conservative`)
- `seller_self_bid | robustness | h5 | kingmaker` -> `meta_switch` (margin `14.4076` over `conservative`)
- `seller_self_bid | robustness | h5 | none` -> `meta_switch` (margin `13.5741` over `level_k`)
- `seller_self_bid | robustness | h10 | herd` -> `meta_switch` (margin `18.1272` over `meta_switch_soft`)
- `seller_self_bid | robustness | h10 | kingmaker` -> `meta_switch` (margin `5.5127` over `meta_switch_soft`)
- `seller_self_bid | robustness | h10 | none` -> `meta_switch` (margin `27.6357` over `level_k`)
- `seller_self_bid | robustness | h10 | respect` -> `meta_switch` (margin `19.5171` over `level_k_l3`)
- `seller_self_bid | robustness | h20 | herd` -> `meta_switch_soft` (margin `35.2262` over `conservative`)
- `seller_self_bid | robustness | h20 | kingmaker` -> `level_k` (margin `10.1700` over `meta_switch_soft`)
- `single_card_sell | ev | h5 | kingmaker` -> `level_k_l3` (margin `1.9334` over `conservative`)
- `single_card_sell | ev | h5 | none` -> `meta_switch_soft` (margin `8.3788` over `meta_switch`)
- `single_card_sell | ev | h5 | respect` -> `meta_switch_soft` (margin `4.7149` over `conservative`)
- `single_card_sell | ev | h10 | kingmaker` -> `level_k_l3` (margin `30.7156` over `meta_switch_soft`)
- `single_card_sell | ev | h10 | respect` -> `meta_switch` (margin `18.5322` over `conservative`)
- `single_card_sell | ev | h20 | kingmaker` -> `meta_switch_soft` (margin `16.1549` over `conservative`)
- `single_card_sell | ev | h20 | respect` -> `meta_switch_soft` (margin `3.4310` over `meta_switch`)
- `single_card_sell | first_place | h5 | herd` -> `pot_fraction` (margin `0.0198` over `meta_switch_soft`)
- `single_card_sell | first_place | h5 | kingmaker` -> `level_k_l3` (margin `0.0294` over `conservative`)
- `single_card_sell | first_place | h5 | none` -> `meta_switch_soft` (margin `0.0281` over `pot_fraction`)
- `single_card_sell | first_place | h5 | respect` -> `meta_switch_soft` (margin `0.1011` over `conservative`)
- `single_card_sell | first_place | h10 | herd` -> `meta_switch` (margin `0.0240` over `meta_switch_soft`)
- `single_card_sell | first_place | h10 | kingmaker` -> `meta_switch` (margin `0.0891` over `conservative`)
- `single_card_sell | first_place | h10 | respect` -> `meta_switch_soft` (margin `0.0186` over `conservative`)
- `single_card_sell | first_place | h20 | kingmaker` -> `meta_switch_soft` (margin `0.0748` over `meta_switch`)
- `single_card_sell | first_place | h20 | respect` -> `pot_fraction` (margin `0.0287` over `conservative`)
- `single_card_sell | robustness | h5 | kingmaker` -> `level_k` (margin `9.8382` over `conservative`)
- `single_card_sell | robustness | h5 | respect` -> `meta_switch` (margin `0.7320` over `level_k_l3`)
- `single_card_sell | robustness | h10 | none` -> `meta_switch` (margin `8.7402` over `meta_switch_soft`)
- `single_card_sell | robustness | h20 | herd` -> `meta_switch_soft` (margin `18.3107` over `level_k_l3`)
- `single_card_sell | robustness | h20 | kingmaker` -> `level_k_l3` (margin `33.4857` over `meta_switch_soft`)
- `single_card_sell | robustness | h20 | none` -> `meta_switch` (margin `10.8819` over `conservative`)
- `single_card_sell | robustness | h20 | respect` -> `meta_switch_soft` (margin `10.9362` over `conservative`)
- `standard_rankings | ev | h5 | none` -> `meta_switch` (margin `6.9730` over `meta_switch_soft`)
- `standard_rankings | ev | h20 | kingmaker` -> `meta_switch_soft` (margin `3.5955` over `conservative`)
- `standard_rankings | robustness | h5 | herd` -> `meta_switch` (margin `22.4840` over `meta_switch_soft`)
- `standard_rankings | robustness | h5 | kingmaker` -> `meta_switch` (margin `16.2257` over `conservative`)
- `standard_rankings | robustness | h5 | none` -> `meta_switch` (margin `25.5298` over `conservative`)
- `standard_rankings | robustness | h10 | herd` -> `meta_switch_soft` (margin `7.0553` over `meta_switch`)
- `standard_rankings | robustness | h10 | kingmaker` -> `meta_switch` (margin `5.6927` over `level_k_l3`)
- `standard_rankings | robustness | h10 | none` -> `meta_switch` (margin `10.0753` over `conservative`)
- `standard_rankings | robustness | h20 | herd` -> `meta_switch_soft` (margin `4.0097` over `meta_switch`)
- `standard_rankings | robustness | h20 | kingmaker` -> `meta_switch` (margin `10.7841` over `conservative`)
- `standard_rankings | robustness | h20 | none` -> `meta_switch` (margin `23.7614` over `conservative`)
- `standard_rankings | robustness | h20 | respect` -> `meta_switch` (margin `15.2925` over `meta_switch_soft`)

## Practical interpretation

- `meta_switch_soft` and `meta_switch` are strong in correlated modes (`respect`, `kingmaker`) and many robustness-targeted scenarios.
- `level_k_l3` appears in some `single_card_sell` variant cases (especially kingmaker-like dynamics).
- `pot_fraction` appears mostly in seller-self-bid + first-place mode pockets and should be used selectively.

## Correlation-strength contingency (baseline h10 focused sweep)

Source:

- `research_logs/experiment_outputs/correlation_sweep_20260301_025118.md`

Summary:

- In a focused candidate pool with evolved `level_k` specs, stronger correlation settings (especially `kingmaker` and `respect`) shifted winners toward tuned `level_k` variants.
- `level_k_l3` and `level_k|level=2|l0_fraction=0.309|tag=levelk_207605` were dominant in most robustness settings as strength increased.
- Practical contingency: if table behavior clearly shows high reciprocal/correlated bidding, use evolved `level_k` variants as override candidates, while keeping `conservative` as global default for uncertain conditions.

## Match-length contingency (baseline h3/h7/h10/h20/h30 sweep)

Source:

- `research_logs/experiment_outputs/long_parallel_matrix_20260301_033913.analysis.json`

Practical guidance:

- Always set HUD `match_horizon` to expected game count so auto condition routing selects the correct `h*` keys.
- For very short matches (`h<=7`), EV and robustness winners skewed toward tuned `level_k` variants (`levelk_base`, `levelk_207605`, `levelk_926417`).
- For longer matches (`h>=20`), tuned `level_k` variants still dominated most EV/robustness scenarios; first-place winners were more mode-dependent and higher-variance.
- If horizon is unknown, keep `match_horizon=10` and rely on objective defaults plus inferred correlation mode.

## Usage in HUD/API

- Load policy map: `POST /strategies/load_policy` with the generated policy JSON.
- Set `policy_condition_key` in recommendations to force condition-specific selection: format `rule_profile|objective|h<horizon>|corr_mode`.
- Optional evolved h10-only policy (tuned `level_k` variants):
  - `research_logs/experiment_outputs/dayof_policy_evolved_h10.json`

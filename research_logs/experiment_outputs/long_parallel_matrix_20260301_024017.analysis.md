# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_024017.json

## Winner counts

- pot_fraction: 4
- levelk_base: 2
- meta_switch_soft: 2
- levelk_42207: 2
- level_k_l3: 1
- level_k: 1

## Winner counts by lcb

- levelk_base: 3
- pot_fraction: 3
- level_k_l3: 1
- conservative: 1
- meta_switch_soft: 1
- level_k: 1
- levelk_207605: 1
- levelk_42207: 1

## Decision table

- baseline_v1 | ev | h=10 | herd -> mean:pot_fraction (expected_pnl=102.8797, ci95=[83.4735,122.2859], margin=3.5056), lcb:level_k_l3
- baseline_v1 | ev | h=10 | kingmaker -> mean:levelk_base (expected_pnl=116.6468, ci95=[107.8171,125.4765], margin=12.0461), lcb:levelk_base
- baseline_v1 | ev | h=10 | none -> mean:level_k_l3 (expected_pnl=133.5049, ci95=[106.6200,160.3898], margin=14.2806), lcb:conservative
- baseline_v1 | ev | h=10 | respect -> mean:meta_switch_soft (expected_pnl=105.1433, ci95=[69.2637,141.0229], margin=0.0383), lcb:levelk_base
- baseline_v1 | first_place | h=10 | herd -> mean:meta_switch_soft (first_place_rate=0.3950, ci95=[0.3509,0.4390], margin=0.0047), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | kingmaker -> mean:pot_fraction (first_place_rate=0.3095, ci95=[0.2715,0.3475], margin=0.0005), lcb:pot_fraction
- baseline_v1 | first_place | h=10 | none -> mean:pot_fraction (first_place_rate=0.3995, ci95=[0.3618,0.4371], margin=0.0305), lcb:pot_fraction
- baseline_v1 | first_place | h=10 | respect -> mean:pot_fraction (first_place_rate=0.3823, ci95=[0.3141,0.4506], margin=0.0333), lcb:pot_fraction
- baseline_v1 | robustness | h=10 | herd -> mean:levelk_base (robustness=57.5084, ci95=[38.0023,77.0144], margin=8.8482), lcb:levelk_base
- baseline_v1 | robustness | h=10 | kingmaker -> mean:level_k (robustness=28.2023, ci95=[15.0734,41.3312], margin=6.3214), lcb:level_k
- baseline_v1 | robustness | h=10 | none -> mean:levelk_42207 (robustness=48.9756, ci95=[27.8615,70.0897], margin=2.1460), lcb:levelk_207605
- baseline_v1 | robustness | h=10 | respect -> mean:levelk_42207 (robustness=28.7853, ci95=[6.2080,51.3625], margin=3.2144), lcb:levelk_42207

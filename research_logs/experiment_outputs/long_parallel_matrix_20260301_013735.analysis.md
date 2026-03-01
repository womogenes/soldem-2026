# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_013735.json

## Winner counts

- conservative: 18
- meta_switch_soft: 14
- meta_switch: 3
- level_k: 1

## Decision table

- baseline_v1 | ev | h=5 | herd -> conservative (expected_pnl=140.0876, margin=0.1239)
- baseline_v1 | ev | h=5 | kingmaker -> conservative (expected_pnl=139.6175, margin=13.8770)
- baseline_v1 | ev | h=5 | none -> meta_switch_soft (expected_pnl=165.2582, margin=3.2033)
- baseline_v1 | ev | h=5 | respect -> conservative (expected_pnl=150.2629, margin=19.4359)
- baseline_v1 | ev | h=10 | herd -> conservative (expected_pnl=154.1352, margin=8.0342)
- baseline_v1 | ev | h=10 | kingmaker -> meta_switch_soft (expected_pnl=141.0864, margin=18.7276)
- baseline_v1 | ev | h=10 | none -> meta_switch_soft (expected_pnl=173.6034, margin=10.9078)
- baseline_v1 | ev | h=10 | respect -> meta_switch_soft (expected_pnl=156.9155, margin=2.5438)
- baseline_v1 | ev | h=20 | herd -> conservative (expected_pnl=138.4442, margin=19.9201)
- baseline_v1 | ev | h=20 | kingmaker -> conservative (expected_pnl=137.0165, margin=17.1515)
- baseline_v1 | ev | h=20 | none -> conservative (expected_pnl=156.9536, margin=5.0724)
- baseline_v1 | ev | h=20 | respect -> conservative (expected_pnl=162.9775, margin=15.5226)
- baseline_v1 | first_place | h=5 | herd -> conservative (first_place_rate=0.4775, margin=0.0670)
- baseline_v1 | first_place | h=5 | kingmaker -> conservative (first_place_rate=0.4024, margin=0.0304)
- baseline_v1 | first_place | h=5 | none -> conservative (first_place_rate=0.4944, margin=0.0319)
- baseline_v1 | first_place | h=5 | respect -> conservative (first_place_rate=0.4832, margin=0.0417)
- baseline_v1 | first_place | h=10 | herd -> meta_switch_soft (first_place_rate=0.4554, margin=0.0071)
- baseline_v1 | first_place | h=10 | kingmaker -> meta_switch_soft (first_place_rate=0.4345, margin=0.0181)
- baseline_v1 | first_place | h=10 | none -> conservative (first_place_rate=0.4942, margin=0.0412)
- baseline_v1 | first_place | h=10 | respect -> meta_switch_soft (first_place_rate=0.4517, margin=0.0730)
- baseline_v1 | first_place | h=20 | herd -> conservative (first_place_rate=0.4704, margin=0.0641)
- baseline_v1 | first_place | h=20 | kingmaker -> meta_switch_soft (first_place_rate=0.4295, margin=0.0336)
- baseline_v1 | first_place | h=20 | none -> meta_switch_soft (first_place_rate=0.4625, margin=0.0025)
- baseline_v1 | first_place | h=20 | respect -> meta_switch_soft (first_place_rate=0.4484, margin=0.0020)
- baseline_v1 | robustness | h=5 | herd -> conservative (robustness=105.4210, margin=15.3432)
- baseline_v1 | robustness | h=5 | kingmaker -> meta_switch (robustness=87.2054, margin=19.8333)
- baseline_v1 | robustness | h=5 | none -> meta_switch_soft (robustness=123.3046, margin=34.4203)
- baseline_v1 | robustness | h=5 | respect -> meta_switch_soft (robustness=87.9317, margin=2.6284)
- baseline_v1 | robustness | h=10 | herd -> conservative (robustness=89.0319, margin=2.3113)
- baseline_v1 | robustness | h=10 | kingmaker -> meta_switch_soft (robustness=76.0479, margin=24.9804)
- baseline_v1 | robustness | h=10 | none -> meta_switch_soft (robustness=134.3824, margin=5.0655)
- baseline_v1 | robustness | h=10 | respect -> level_k (robustness=73.3651, margin=6.7432)
- baseline_v1 | robustness | h=20 | herd -> meta_switch (robustness=97.8175, margin=0.1662)
- baseline_v1 | robustness | h=20 | kingmaker -> conservative (robustness=93.2734, margin=24.3103)
- baseline_v1 | robustness | h=20 | none -> conservative (robustness=112.2601, margin=0.5307)
- baseline_v1 | robustness | h=20 | respect -> meta_switch (robustness=119.5703, margin=12.7613)

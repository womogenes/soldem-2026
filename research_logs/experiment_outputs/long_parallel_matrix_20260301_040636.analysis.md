# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_040636.json

## Winner counts

- level_k_l3: 3
- levelk_207605: 2
- meta_switch_soft: 2
- level_k: 2
- bully: 1
- levelk_base: 1
- levelk_926417: 1

## Winner counts by lcb

- bully: 3
- level_k_l3: 2
- levelk_926417: 2
- levelk_42207: 1
- meta_switch_soft: 1
- levelk_base: 1
- levelk_207605: 1
- level_k: 1

## Decision table

- baseline_v1 | first_place | h=5 | herd -> mean:bully (first_place_rate=0.2276, ci95=[0.2014,0.2539], margin=0.0114), lcb:bully
- baseline_v1 | first_place | h=5 | kingmaker -> mean:level_k_l3 (first_place_rate=0.2314, ci95=[0.2123,0.2505], margin=0.0037), lcb:level_k_l3
- baseline_v1 | first_place | h=5 | none -> mean:levelk_207605 (first_place_rate=0.2467, ci95=[0.2017,0.2917], margin=0.0099), lcb:levelk_42207
- baseline_v1 | first_place | h=5 | respect -> mean:meta_switch_soft (first_place_rate=0.2465, ci95=[0.2005,0.2926], margin=0.0108), lcb:level_k_l3
- baseline_v1 | first_place | h=10 | herd -> mean:level_k_l3 (first_place_rate=0.2219, ci95=[0.1962,0.2476], margin=0.0012), lcb:bully
- baseline_v1 | first_place | h=10 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.2364, ci95=[0.2097,0.2631], margin=0.0006), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | none -> mean:levelk_base (first_place_rate=0.2584, ci95=[0.2433,0.2734], margin=0.0165), lcb:levelk_base
- baseline_v1 | first_place | h=10 | respect -> mean:levelk_926417 (first_place_rate=0.2412, ci95=[0.2082,0.2743], margin=0.0045), lcb:levelk_926417
- baseline_v1 | first_place | h=20 | herd -> mean:level_k (first_place_rate=0.2291, ci95=[0.1920,0.2663], margin=0.0024), lcb:bully
- baseline_v1 | first_place | h=20 | kingmaker -> mean:level_k_l3 (first_place_rate=0.2399, ci95=[0.2173,0.2625], margin=0.0046), lcb:levelk_926417
- baseline_v1 | first_place | h=20 | none -> mean:levelk_207605 (first_place_rate=0.2344, ci95=[0.2216,0.2473], margin=0.0005), lcb:levelk_207605
- baseline_v1 | first_place | h=20 | respect -> mean:level_k (first_place_rate=0.2529, ci95=[0.2441,0.2617], margin=0.0208), lcb:level_k

# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_023315.json

## Winner counts

- levelk_42207: 3
- levelk_207605: 3
- level_k: 3
- levelk_926417: 2
- levelk_base: 1

## Winner counts by lcb

- levelk_42207: 3
- levelk_207605: 3
- levelk_base: 3
- level_k: 2
- levelk_926417: 1

## Decision table

- baseline_v1 | ev | h=10 | herd -> mean:levelk_42207 (expected_pnl=21.7133, ci95=[14.4776,28.9490], margin=4.7122), lcb:levelk_42207
- baseline_v1 | ev | h=10 | kingmaker -> mean:levelk_207605 (expected_pnl=29.6686, ci95=[21.1303,38.2069], margin=4.6525), lcb:levelk_207605
- baseline_v1 | ev | h=10 | none -> mean:levelk_42207 (expected_pnl=27.9565, ci95=[17.5266,38.3863], margin=1.4378), lcb:levelk_42207
- baseline_v1 | ev | h=10 | respect -> mean:level_k (expected_pnl=31.5491, ci95=[21.6356,41.4625], margin=5.1360), lcb:level_k
- baseline_v1 | first_place | h=10 | herd -> mean:levelk_926417 (first_place_rate=0.2447, ci95=[0.2100,0.2795], margin=0.0027), lcb:levelk_base
- baseline_v1 | first_place | h=10 | kingmaker -> mean:level_k (first_place_rate=0.2438, ci95=[0.1818,0.3059], margin=0.0123), lcb:levelk_base
- baseline_v1 | first_place | h=10 | none -> mean:levelk_926417 (first_place_rate=0.2540, ci95=[0.2097,0.2982], margin=0.0194), lcb:levelk_926417
- baseline_v1 | first_place | h=10 | respect -> mean:levelk_base (first_place_rate=0.2456, ci95=[0.2223,0.2689], margin=0.0079), lcb:levelk_base
- baseline_v1 | robustness | h=10 | herd -> mean:level_k (robustness=-77.7944, ci95=[-91.7091,-63.8798], margin=4.6260), lcb:level_k
- baseline_v1 | robustness | h=10 | kingmaker -> mean:levelk_207605 (robustness=-64.4390, ci95=[-76.8438,-52.0342], margin=6.7109), lcb:levelk_207605
- baseline_v1 | robustness | h=10 | none -> mean:levelk_207605 (robustness=-74.5498, ci95=[-92.7468,-56.3529], margin=10.5444), lcb:levelk_207605
- baseline_v1 | robustness | h=10 | respect -> mean:levelk_42207 (robustness=-81.7912, ci95=[-94.1840,-69.3984], margin=0.3907), lcb:levelk_42207

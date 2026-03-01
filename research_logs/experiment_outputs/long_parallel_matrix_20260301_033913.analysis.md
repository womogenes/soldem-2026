# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_033913.json

## Winner counts

- levelk_base: 13
- levelk_926417: 12
- levelk_207605: 8
- level_k: 8
- levelk_42207: 6
- level_k_l3: 5
- bully: 3
- meta_switch_soft: 3
- meta_switch: 2

## Winner counts by lcb

- levelk_926417: 11
- levelk_base: 10
- level_k: 9
- levelk_42207: 9
- levelk_207605: 6
- meta_switch_soft: 6
- level_k_l3: 4
- bully: 3
- adaptive_profile: 1
- meta_switch: 1

## Decision table

- baseline_v1 | ev | h=3 | herd -> mean:levelk_base (expected_pnl=36.0349, ci95=[30.3493,41.7204], margin=4.4763), lcb:levelk_base
- baseline_v1 | ev | h=3 | kingmaker -> mean:levelk_207605 (expected_pnl=47.6484, ci95=[36.0622,59.2346], margin=1.0086), lcb:levelk_207605
- baseline_v1 | ev | h=3 | none -> mean:level_k (expected_pnl=55.7808, ci95=[51.0003,60.5613], margin=5.8256), lcb:level_k
- baseline_v1 | ev | h=3 | respect -> mean:levelk_926417 (expected_pnl=65.0822, ci95=[41.8861,88.2783], margin=13.2879), lcb:meta_switch_soft
- baseline_v1 | ev | h=7 | herd -> mean:levelk_base (expected_pnl=36.6111, ci95=[27.1602,46.0620], margin=3.0689), lcb:levelk_base
- baseline_v1 | ev | h=7 | kingmaker -> mean:levelk_926417 (expected_pnl=54.1792, ci95=[38.9206,69.4379], margin=9.5036), lcb:levelk_926417
- baseline_v1 | ev | h=7 | none -> mean:level_k_l3 (expected_pnl=47.9573, ci95=[20.7273,75.1873], margin=1.3607), lcb:levelk_926417
- baseline_v1 | ev | h=7 | respect -> mean:levelk_42207 (expected_pnl=47.0208, ci95=[37.9619,56.0796], margin=4.3858), lcb:levelk_42207
- baseline_v1 | ev | h=10 | herd -> mean:levelk_926417 (expected_pnl=36.8636, ci95=[31.7515,41.9758], margin=0.8292), lcb:levelk_926417
- baseline_v1 | ev | h=10 | kingmaker -> mean:levelk_926417 (expected_pnl=43.1875, ci95=[29.0542,57.3207], margin=0.7755), lcb:levelk_926417
- baseline_v1 | ev | h=10 | none -> mean:level_k_l3 (expected_pnl=51.4534, ci95=[35.4013,67.5056], margin=1.7986), lcb:level_k_l3
- baseline_v1 | ev | h=10 | respect -> mean:level_k (expected_pnl=56.9789, ci95=[50.9270,63.0308], margin=1.2212), lcb:level_k
- baseline_v1 | ev | h=20 | herd -> mean:levelk_base (expected_pnl=41.8619, ci95=[37.7837,45.9402], margin=7.0565), lcb:levelk_base
- baseline_v1 | ev | h=20 | kingmaker -> mean:levelk_base (expected_pnl=49.2279, ci95=[41.6076,56.8482], margin=6.3938), lcb:levelk_base
- baseline_v1 | ev | h=20 | none -> mean:levelk_207605 (expected_pnl=49.4568, ci95=[32.1409,66.7727], margin=2.2246), lcb:levelk_base
- baseline_v1 | ev | h=20 | respect -> mean:levelk_207605 (expected_pnl=50.6814, ci95=[43.4284,57.9344], margin=5.1951), lcb:levelk_207605
- baseline_v1 | ev | h=30 | herd -> mean:level_k_l3 (expected_pnl=40.2165, ci95=[26.5623,53.8707], margin=2.8874), lcb:meta_switch_soft
- baseline_v1 | ev | h=30 | kingmaker -> mean:levelk_base (expected_pnl=42.0084, ci95=[22.3600,61.6568], margin=1.7727), lcb:level_k_l3
- baseline_v1 | ev | h=30 | none -> mean:levelk_207605 (expected_pnl=52.2564, ci95=[30.4072,74.1057], margin=3.5460), lcb:levelk_base
- baseline_v1 | ev | h=30 | respect -> mean:levelk_base (expected_pnl=52.7428, ci95=[38.9682,66.5174], margin=8.2137), lcb:levelk_base
- baseline_v1 | first_place | h=3 | herd -> mean:bully (first_place_rate=0.2338, ci95=[0.2035,0.2641], margin=0.0048), lcb:adaptive_profile
- baseline_v1 | first_place | h=3 | kingmaker -> mean:levelk_base (first_place_rate=0.2473, ci95=[0.2034,0.2913], margin=0.0000), lcb:meta_switch
- baseline_v1 | first_place | h=3 | none -> mean:meta_switch_soft (first_place_rate=0.2594, ci95=[0.2264,0.2924], margin=0.0164), lcb:meta_switch_soft
- baseline_v1 | first_place | h=3 | respect -> mean:level_k_l3 (first_place_rate=0.2733, ci95=[0.2548,0.2918], margin=0.0153), lcb:level_k_l3
- baseline_v1 | first_place | h=7 | herd -> mean:levelk_207605 (first_place_rate=0.2293, ci95=[0.2073,0.2513], margin=0.0010), lcb:bully
- baseline_v1 | first_place | h=7 | kingmaker -> mean:levelk_base (first_place_rate=0.2384, ci95=[0.2139,0.2628], margin=0.0003), lcb:levelk_base
- baseline_v1 | first_place | h=7 | none -> mean:levelk_base (first_place_rate=0.2925, ci95=[0.2468,0.3382], margin=0.0347), lcb:levelk_base
- baseline_v1 | first_place | h=7 | respect -> mean:levelk_42207 (first_place_rate=0.2642, ci95=[0.2306,0.2978], margin=0.0080), lcb:levelk_42207
- baseline_v1 | first_place | h=10 | herd -> mean:bully (first_place_rate=0.2278, ci95=[0.2201,0.2356], margin=0.0054), lcb:bully
- baseline_v1 | first_place | h=10 | kingmaker -> mean:levelk_42207 (first_place_rate=0.2563, ci95=[0.2347,0.2778], margin=0.0024), lcb:level_k
- baseline_v1 | first_place | h=10 | none -> mean:meta_switch (first_place_rate=0.2770, ci95=[0.2302,0.3238], margin=0.0111), lcb:level_k
- baseline_v1 | first_place | h=10 | respect -> mean:levelk_base (first_place_rate=0.2622, ci95=[0.1864,0.3380], margin=0.0228), lcb:meta_switch_soft
- baseline_v1 | first_place | h=20 | herd -> mean:levelk_926417 (first_place_rate=0.2317, ci95=[0.1661,0.2973], margin=0.0049), lcb:levelk_42207
- baseline_v1 | first_place | h=20 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.2529, ci95=[0.2251,0.2807], margin=0.0109), lcb:meta_switch_soft
- baseline_v1 | first_place | h=20 | none -> mean:meta_switch (first_place_rate=0.2945, ci95=[0.2336,0.3553], margin=0.0230), lcb:levelk_42207
- baseline_v1 | first_place | h=20 | respect -> mean:level_k (first_place_rate=0.2597, ci95=[0.2553,0.2641], margin=0.0135), lcb:level_k
- baseline_v1 | first_place | h=30 | herd -> mean:bully (first_place_rate=0.2547, ci95=[0.2397,0.2697], margin=0.0104), lcb:bully
- baseline_v1 | first_place | h=30 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.2522, ci95=[0.2176,0.2868], margin=0.0180), lcb:meta_switch_soft
- baseline_v1 | first_place | h=30 | none -> mean:level_k (first_place_rate=0.2736, ci95=[0.2182,0.3290], margin=0.0230), lcb:levelk_926417
- baseline_v1 | first_place | h=30 | respect -> mean:levelk_207605 (first_place_rate=0.2630, ci95=[0.2328,0.2933], margin=0.0125), lcb:levelk_207605
- baseline_v1 | robustness | h=3 | herd -> mean:levelk_926417 (robustness=-53.2358, ci95=[-64.0342,-42.4374], margin=0.7673), lcb:level_k
- baseline_v1 | robustness | h=3 | kingmaker -> mean:levelk_926417 (robustness=-50.3714, ci95=[-59.9709,-40.7719], margin=2.5569), lcb:levelk_926417
- baseline_v1 | robustness | h=3 | none -> mean:levelk_926417 (robustness=-47.8656, ci95=[-64.7561,-30.9751], margin=10.4459), lcb:levelk_926417
- baseline_v1 | robustness | h=3 | respect -> mean:level_k (robustness=-68.2391, ci95=[-85.3437,-51.1346], margin=0.2496), lcb:levelk_207605
- baseline_v1 | robustness | h=7 | herd -> mean:levelk_207605 (robustness=-61.8728, ci95=[-71.8611,-51.8844], margin=0.1395), lcb:levelk_207605
- baseline_v1 | robustness | h=7 | kingmaker -> mean:levelk_base (robustness=-48.6898, ci95=[-68.7745,-28.6050], margin=0.3702), lcb:levelk_42207
- baseline_v1 | robustness | h=7 | none -> mean:levelk_207605 (robustness=-37.6486, ci95=[-67.3785,-7.9187], margin=2.8960), lcb:level_k
- baseline_v1 | robustness | h=7 | respect -> mean:levelk_42207 (robustness=-41.0510, ci95=[-54.7734,-27.3286], margin=19.6653), lcb:levelk_42207
- baseline_v1 | robustness | h=10 | herd -> mean:level_k (robustness=-68.1808, ci95=[-88.3316,-48.0299], margin=1.4695), lcb:levelk_207605
- baseline_v1 | robustness | h=10 | kingmaker -> mean:levelk_926417 (robustness=-42.2819, ci95=[-49.5323,-35.0315], margin=7.5714), lcb:levelk_926417
- baseline_v1 | robustness | h=10 | none -> mean:levelk_926417 (robustness=-53.1864, ci95=[-62.1674,-44.2054], margin=9.8432), lcb:levelk_926417
- baseline_v1 | robustness | h=10 | respect -> mean:level_k (robustness=-58.3852, ci95=[-65.5477,-51.2227], margin=2.9630), lcb:level_k
- baseline_v1 | robustness | h=20 | herd -> mean:levelk_42207 (robustness=-58.1942, ci95=[-80.0569,-36.3316], margin=2.2786), lcb:levelk_42207
- baseline_v1 | robustness | h=20 | kingmaker -> mean:level_k_l3 (robustness=-49.9868, ci95=[-74.0880,-25.8856], margin=5.5066), lcb:levelk_42207
- baseline_v1 | robustness | h=20 | none -> mean:levelk_base (robustness=-52.5597, ci95=[-108.6633,3.5440], margin=5.5675), lcb:levelk_926417
- baseline_v1 | robustness | h=20 | respect -> mean:levelk_42207 (robustness=-58.1200, ci95=[-79.9369,-36.3031], margin=3.6685), lcb:levelk_42207
- baseline_v1 | robustness | h=30 | herd -> mean:level_k (robustness=-58.2116, ci95=[-72.9128,-43.5105], margin=3.3720), lcb:level_k
- baseline_v1 | robustness | h=30 | kingmaker -> mean:levelk_926417 (robustness=-51.8969, ci95=[-63.2122,-40.5817], margin=4.8666), lcb:levelk_base
- baseline_v1 | robustness | h=30 | none -> mean:levelk_base (robustness=-56.8429, ci95=[-74.5534,-39.1324], margin=2.7840), lcb:level_k_l3
- baseline_v1 | robustness | h=30 | respect -> mean:levelk_926417 (robustness=-57.3795, ci95=[-59.3638,-55.3953], margin=2.2523), lcb:levelk_926417

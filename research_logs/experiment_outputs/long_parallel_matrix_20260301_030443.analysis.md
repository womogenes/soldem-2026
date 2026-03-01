# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_030443.json

## Winner counts

- levelk_207605: 9
- level_k_l3: 8
- levelk_base: 8
- levelk_42207: 7
- level_k: 4
- levelk_926417: 4
- bully: 3
- meta_switch_soft: 2
- meta_switch: 1
- pot_fraction: 1
- conservative: 1

## Winner counts by lcb

- levelk_207605: 12
- level_k_l3: 9
- levelk_base: 8
- levelk_42207: 6
- level_k: 4
- bully: 2
- meta_switch_soft: 2
- levelk_926417: 2
- pot_fraction: 1
- conservative: 1
- meta_switch: 1

## Decision table

- baseline_v1 | ev | h=10 | herd -> mean:levelk_42207 (expected_pnl=40.7696, ci95=[32.8199,48.7193], margin=9.2694), lcb:levelk_42207
- baseline_v1 | ev | h=10 | kingmaker -> mean:level_k_l3 (expected_pnl=44.1496, ci95=[34.9041,53.3950], margin=1.1268), lcb:level_k_l3
- baseline_v1 | ev | h=10 | none -> mean:meta_switch (expected_pnl=46.2479, ci95=[38.1234,54.3725], margin=0.1406), lcb:levelk_207605
- baseline_v1 | ev | h=10 | respect -> mean:levelk_207605 (expected_pnl=52.6486, ci95=[28.3170,76.9801], margin=9.5624), lcb:levelk_42207
- baseline_v1 | first_place | h=10 | herd -> mean:bully (first_place_rate=0.2352, ci95=[0.2162,0.2542], margin=0.0131), lcb:bully
- baseline_v1 | first_place | h=10 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.2386, ci95=[0.2170,0.2602], margin=0.0022), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | none -> mean:level_k (first_place_rate=0.2576, ci95=[0.2325,0.2826], margin=0.0100), lcb:level_k
- baseline_v1 | first_place | h=10 | respect -> mean:level_k_l3 (first_place_rate=0.2628, ci95=[0.2402,0.2855], margin=0.0205), lcb:level_k_l3
- baseline_v1 | robustness | h=10 | herd -> mean:level_k_l3 (robustness=-70.6256, ci95=[-84.4267,-56.8245], margin=0.8639), lcb:level_k_l3
- baseline_v1 | robustness | h=10 | kingmaker -> mean:levelk_207605 (robustness=-49.5366, ci95=[-61.8428,-37.2305], margin=0.5667), lcb:levelk_207605
- baseline_v1 | robustness | h=10 | none -> mean:levelk_42207 (robustness=-61.3829, ci95=[-77.8813,-44.8844], margin=1.0183), lcb:levelk_207605
- baseline_v1 | robustness | h=10 | respect -> mean:levelk_base (robustness=-57.6617, ci95=[-64.4436,-50.8799], margin=11.3535), lcb:levelk_base
- seller_self_bid | ev | h=10 | herd -> mean:levelk_207605 (expected_pnl=25.5553, ci95=[15.3246,35.7859], margin=1.1196), lcb:levelk_207605
- seller_self_bid | ev | h=10 | kingmaker -> mean:levelk_42207 (expected_pnl=48.2903, ci95=[42.7142,53.8665], margin=2.9414), lcb:levelk_42207
- seller_self_bid | ev | h=10 | none -> mean:levelk_207605 (expected_pnl=55.8094, ci95=[46.4473,65.1715], margin=12.5794), lcb:levelk_207605
- seller_self_bid | ev | h=10 | respect -> mean:level_k (expected_pnl=41.9456, ci95=[29.9817,53.9094], margin=2.3620), lcb:level_k
- seller_self_bid | first_place | h=10 | herd -> mean:pot_fraction (first_place_rate=0.2451, ci95=[0.2301,0.2601], margin=0.0244), lcb:pot_fraction
- seller_self_bid | first_place | h=10 | kingmaker -> mean:levelk_42207 (first_place_rate=0.2517, ci95=[0.2164,0.2870], margin=0.0094), lcb:levelk_926417
- seller_self_bid | first_place | h=10 | none -> mean:conservative (first_place_rate=0.2429, ci95=[0.2333,0.2526], margin=0.0117), lcb:conservative
- seller_self_bid | first_place | h=10 | respect -> mean:levelk_926417 (first_place_rate=0.2429, ci95=[0.2075,0.2783], margin=0.0126), lcb:level_k_l3
- seller_self_bid | robustness | h=10 | herd -> mean:levelk_207605 (robustness=-74.2855, ci95=[-82.1662,-66.4048], margin=1.5302), lcb:levelk_207605
- seller_self_bid | robustness | h=10 | kingmaker -> mean:level_k (robustness=-71.3196, ci95=[-88.8783,-53.7609], margin=2.4028), lcb:level_k
- seller_self_bid | robustness | h=10 | none -> mean:levelk_base (robustness=-62.8002, ci95=[-82.9119,-42.6885], margin=3.7339), lcb:levelk_base
- seller_self_bid | robustness | h=10 | respect -> mean:levelk_base (robustness=-53.2668, ci95=[-67.1805,-39.3530], margin=10.2258), lcb:levelk_base
- single_card_sell | ev | h=10 | herd -> mean:levelk_926417 (expected_pnl=33.4321, ci95=[23.4722,43.3921], margin=1.3472), lcb:level_k_l3
- single_card_sell | ev | h=10 | kingmaker -> mean:levelk_base (expected_pnl=49.6087, ci95=[36.5262,62.6911], margin=7.2279), lcb:levelk_base
- single_card_sell | ev | h=10 | none -> mean:levelk_926417 (expected_pnl=45.7070, ci95=[20.1973,71.2166], margin=1.9620), lcb:levelk_207605
- single_card_sell | ev | h=10 | respect -> mean:levelk_base (expected_pnl=50.4383, ci95=[42.1079,58.7687], margin=1.9261), lcb:levelk_base
- single_card_sell | first_place | h=10 | herd -> mean:bully (first_place_rate=0.2376, ci95=[0.2207,0.2544], margin=0.0019), lcb:meta_switch_soft
- single_card_sell | first_place | h=10 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.2407, ci95=[0.2116,0.2699], margin=0.0046), lcb:levelk_207605
- single_card_sell | first_place | h=10 | none -> mean:levelk_42207 (first_place_rate=0.2532, ci95=[0.2084,0.2979], margin=0.0117), lcb:meta_switch
- single_card_sell | first_place | h=10 | respect -> mean:level_k_l3 (first_place_rate=0.2517, ci95=[0.2120,0.2913], margin=0.0018), lcb:levelk_base
- single_card_sell | robustness | h=10 | herd -> mean:level_k_l3 (robustness=-67.6113, ci95=[-85.8791,-49.3435], margin=1.1292), lcb:levelk_926417
- single_card_sell | robustness | h=10 | kingmaker -> mean:levelk_base (robustness=-43.5347, ci95=[-54.1306,-32.9388], margin=13.9469), lcb:levelk_base
- single_card_sell | robustness | h=10 | none -> mean:levelk_42207 (robustness=-48.0311, ci95=[-58.5778,-37.4845], margin=14.6517), lcb:levelk_42207
- single_card_sell | robustness | h=10 | respect -> mean:levelk_207605 (robustness=-60.5971, ci95=[-73.6345,-47.5597], margin=7.9941), lcb:levelk_207605
- standard_rankings | ev | h=10 | herd -> mean:level_k_l3 (expected_pnl=31.5820, ci95=[23.4441,39.7198], margin=1.0646), lcb:level_k_l3
- standard_rankings | ev | h=10 | kingmaker -> mean:levelk_base (expected_pnl=48.8685, ci95=[35.1499,62.5871], margin=4.6611), lcb:level_k_l3
- standard_rankings | ev | h=10 | none -> mean:levelk_207605 (expected_pnl=44.6808, ci95=[41.7478,47.6138], margin=2.2069), lcb:levelk_207605
- standard_rankings | ev | h=10 | respect -> mean:levelk_base (expected_pnl=40.9340, ci95=[31.4806,50.3873], margin=0.8547), lcb:levelk_base
- standard_rankings | first_place | h=10 | herd -> mean:bully (first_place_rate=0.2515, ci95=[0.2260,0.2770], margin=0.0098), lcb:bully
- standard_rankings | first_place | h=10 | kingmaker -> mean:level_k_l3 (first_place_rate=0.2685, ci95=[0.2380,0.2991], margin=0.0147), lcb:level_k_l3
- standard_rankings | first_place | h=10 | none -> mean:levelk_207605 (first_place_rate=0.2690, ci95=[0.2527,0.2853], margin=0.0155), lcb:levelk_207605
- standard_rankings | first_place | h=10 | respect -> mean:level_k (first_place_rate=0.2447, ci95=[0.2338,0.2557], margin=0.0108), lcb:level_k
- standard_rankings | robustness | h=10 | herd -> mean:levelk_926417 (robustness=-76.1260, ci95=[-90.6604,-61.5916], margin=1.3881), lcb:levelk_42207
- standard_rankings | robustness | h=10 | kingmaker -> mean:levelk_42207 (robustness=-63.9358, ci95=[-77.1591,-50.7125], margin=1.0906), lcb:levelk_42207
- standard_rankings | robustness | h=10 | none -> mean:level_k_l3 (robustness=-67.8316, ci95=[-77.9214,-57.7417], margin=2.2861), lcb:level_k_l3
- standard_rankings | robustness | h=10 | respect -> mean:levelk_207605 (robustness=-65.2096, ci95=[-75.1162,-55.3030], margin=1.9498), lcb:levelk_207605

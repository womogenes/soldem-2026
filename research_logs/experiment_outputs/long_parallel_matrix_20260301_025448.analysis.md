# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_025448.json

## Winner counts

- meta_switch_soft: 14
- levelk_926417: 4
- conservative: 4
- levelk_base: 4
- pot_fraction: 3
- levelk_42207: 2
- meta_switch: 2
- levelk_207605: 2
- level_k: 1

## Winner counts by lcb

- meta_switch_soft: 10
- levelk_207605: 5
- levelk_base: 5
- level_k_l3: 4
- level_k: 3
- pot_fraction: 3
- conservative: 2
- levelk_42207: 2
- levelk_926417: 2

## Decision table

- baseline_v1 | ev | h=5 | herd -> mean:meta_switch_soft (expected_pnl=101.4764, ci95=[73.3894,129.5635], margin=5.7786), lcb:conservative
- baseline_v1 | ev | h=5 | kingmaker -> mean:levelk_42207 (expected_pnl=94.4130, ci95=[81.3259,107.5002], margin=0.4084), lcb:levelk_42207
- baseline_v1 | ev | h=5 | none -> mean:levelk_926417 (expected_pnl=114.6868, ci95=[98.6311,130.7426], margin=1.7501), lcb:levelk_207605
- baseline_v1 | ev | h=5 | respect -> mean:meta_switch_soft (expected_pnl=109.1039, ci95=[104.4636,113.7442], margin=1.6037), lcb:meta_switch_soft
- baseline_v1 | ev | h=10 | herd -> mean:conservative (expected_pnl=117.0784, ci95=[98.7683,135.3884], margin=0.9074), lcb:meta_switch_soft
- baseline_v1 | ev | h=10 | kingmaker -> mean:meta_switch_soft (expected_pnl=111.0686, ci95=[87.8128,134.3244], margin=6.4819), lcb:level_k_l3
- baseline_v1 | ev | h=10 | none -> mean:conservative (expected_pnl=121.4834, ci95=[108.3206,134.6462], margin=6.8805), lcb:conservative
- baseline_v1 | ev | h=10 | respect -> mean:meta_switch (expected_pnl=113.2984, ci95=[82.0327,144.5642], margin=2.9172), lcb:level_k_l3
- baseline_v1 | ev | h=20 | herd -> mean:levelk_base (expected_pnl=104.0814, ci95=[89.5166,118.6463], margin=3.1521), lcb:levelk_base
- baseline_v1 | ev | h=20 | kingmaker -> mean:levelk_926417 (expected_pnl=108.1603, ci95=[90.3064,126.0142], margin=12.8058), lcb:levelk_926417
- baseline_v1 | ev | h=20 | none -> mean:meta_switch_soft (expected_pnl=116.9329, ci95=[96.2085,137.6572], margin=3.4873), lcb:level_k
- baseline_v1 | ev | h=20 | respect -> mean:meta_switch_soft (expected_pnl=120.9161, ci95=[108.3348,133.4974], margin=6.8521), lcb:meta_switch_soft
- baseline_v1 | first_place | h=5 | herd -> mean:meta_switch_soft (first_place_rate=0.3566, ci95=[0.3243,0.3890], margin=0.0018), lcb:meta_switch_soft
- baseline_v1 | first_place | h=5 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.3517, ci95=[0.2343,0.4692], margin=0.0174), lcb:level_k
- baseline_v1 | first_place | h=5 | none -> mean:meta_switch_soft (first_place_rate=0.3723, ci95=[0.3577,0.3869], margin=0.0214), lcb:meta_switch_soft
- baseline_v1 | first_place | h=5 | respect -> mean:meta_switch_soft (first_place_rate=0.3661, ci95=[0.3273,0.4049], margin=0.0523), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | herd -> mean:pot_fraction (first_place_rate=0.3687, ci95=[0.3526,0.3848], margin=0.0238), lcb:pot_fraction
- baseline_v1 | first_place | h=10 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.3319, ci95=[0.3027,0.3611], margin=0.0186), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | none -> mean:meta_switch_soft (first_place_rate=0.3866, ci95=[0.3420,0.4313], margin=0.0149), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | respect -> mean:pot_fraction (first_place_rate=0.3302, ci95=[0.3079,0.3526], margin=0.0084), lcb:pot_fraction
- baseline_v1 | first_place | h=20 | herd -> mean:pot_fraction (first_place_rate=0.3284, ci95=[0.3077,0.3491], margin=0.0078), lcb:pot_fraction
- baseline_v1 | first_place | h=20 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.3163, ci95=[0.2500,0.3827], margin=0.0157), lcb:levelk_207605
- baseline_v1 | first_place | h=20 | none -> mean:conservative (first_place_rate=0.3679, ci95=[0.2883,0.4475], margin=0.0245), lcb:level_k_l3
- baseline_v1 | first_place | h=20 | respect -> mean:meta_switch_soft (first_place_rate=0.3673, ci95=[0.3395,0.3951], margin=0.0064), lcb:meta_switch_soft
- baseline_v1 | robustness | h=5 | herd -> mean:meta_switch_soft (robustness=36.5958, ci95=[19.5542,53.6373], margin=15.0068), lcb:meta_switch_soft
- baseline_v1 | robustness | h=5 | kingmaker -> mean:level_k (robustness=31.4429, ci95=[2.2898,60.5959], margin=8.1766), lcb:level_k
- baseline_v1 | robustness | h=5 | none -> mean:levelk_207605 (robustness=47.2081, ci95=[32.8524,61.5637], margin=13.8509), lcb:levelk_207605
- baseline_v1 | robustness | h=5 | respect -> mean:levelk_base (robustness=25.8459, ci95=[8.0500,43.6418], margin=0.5492), lcb:levelk_base
- baseline_v1 | robustness | h=10 | herd -> mean:conservative (robustness=18.5375, ci95=[-18.2405,55.3155], margin=2.1821), lcb:levelk_base
- baseline_v1 | robustness | h=10 | kingmaker -> mean:levelk_42207 (robustness=44.8319, ci95=[7.6342,82.0296], margin=24.7959), lcb:levelk_42207
- baseline_v1 | robustness | h=10 | none -> mean:levelk_base (robustness=40.9511, ci95=[18.0676,63.8346], margin=11.4976), lcb:levelk_base
- baseline_v1 | robustness | h=10 | respect -> mean:levelk_207605 (robustness=40.6218, ci95=[17.5711,63.6725], margin=10.3336), lcb:levelk_207605
- baseline_v1 | robustness | h=20 | herd -> mean:levelk_926417 (robustness=20.9070, ci95=[-0.7337,42.5477], margin=5.8817), lcb:levelk_base
- baseline_v1 | robustness | h=20 | kingmaker -> mean:levelk_base (robustness=20.7090, ci95=[-2.5630,43.9811], margin=4.8723), lcb:levelk_207605
- baseline_v1 | robustness | h=20 | none -> mean:meta_switch (robustness=34.0179, ci95=[2.6598,65.3760], margin=0.0948), lcb:levelk_926417
- baseline_v1 | robustness | h=20 | respect -> mean:levelk_926417 (robustness=29.1271, ci95=[9.7398,48.5144], margin=1.1380), lcb:level_k_l3

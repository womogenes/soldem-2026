# Long matrix analysis

Source: research_logs/experiment_outputs/long_parallel_matrix_20260301_020705.json

## Winner counts

- conservative: 31
- meta_switch: 9
- meta_switch_soft: 8

## Winner counts by lcb

- conservative: 31
- meta_switch_soft: 10
- meta_switch: 7

## Decision table

- baseline_v1 | ev | h=10 | herd -> mean:conservative (expected_pnl=155.4755, ci95=[146.7448,164.2062], margin=10.3703), lcb:conservative
- baseline_v1 | ev | h=10 | kingmaker -> mean:conservative (expected_pnl=146.6052, ci95=[137.7898,155.4206], margin=3.3836), lcb:conservative
- baseline_v1 | ev | h=10 | none -> mean:conservative (expected_pnl=166.4670, ci95=[157.7968,175.1372], margin=5.6221), lcb:conservative
- baseline_v1 | ev | h=10 | respect -> mean:conservative (expected_pnl=147.7880, ci95=[139.3227,156.2533], margin=7.3044), lcb:conservative
- baseline_v1 | first_place | h=10 | herd -> mean:conservative (first_place_rate=0.4778, ci95=[0.4361,0.5195], margin=0.0506), lcb:conservative
- baseline_v1 | first_place | h=10 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.4357, ci95=[0.4159,0.4555], margin=0.0169), lcb:meta_switch_soft
- baseline_v1 | first_place | h=10 | none -> mean:conservative (first_place_rate=0.5112, ci95=[0.4814,0.5409], margin=0.0064), lcb:conservative
- baseline_v1 | first_place | h=10 | respect -> mean:meta_switch_soft (first_place_rate=0.4818, ci95=[0.4723,0.4913], margin=0.0065), lcb:meta_switch_soft
- baseline_v1 | robustness | h=10 | herd -> mean:meta_switch_soft (robustness=137.0678, ci95=[119.7732,154.3624], margin=21.3450), lcb:meta_switch_soft
- baseline_v1 | robustness | h=10 | kingmaker -> mean:meta_switch (robustness=79.2612, ci95=[66.8412,91.6813], margin=3.4326), lcb:meta_switch
- baseline_v1 | robustness | h=10 | none -> mean:conservative (robustness=131.4879, ci95=[108.3583,154.6174], margin=14.9477), lcb:conservative
- baseline_v1 | robustness | h=10 | respect -> mean:conservative (robustness=129.1975, ci95=[113.4030,144.9919], margin=27.0474), lcb:conservative
- seller_self_bid | ev | h=10 | herd -> mean:conservative (expected_pnl=159.0410, ci95=[151.3722,166.7098], margin=15.6308), lcb:conservative
- seller_self_bid | ev | h=10 | kingmaker -> mean:conservative (expected_pnl=144.5307, ci95=[130.0211,159.0403], margin=21.3357), lcb:conservative
- seller_self_bid | ev | h=10 | none -> mean:conservative (expected_pnl=180.6450, ci95=[172.5722,188.7178], margin=22.1930), lcb:conservative
- seller_self_bid | ev | h=10 | respect -> mean:conservative (expected_pnl=157.5488, ci95=[148.2836,166.8139], margin=19.6026), lcb:conservative
- seller_self_bid | first_place | h=10 | herd -> mean:conservative (first_place_rate=0.4551, ci95=[0.4356,0.4747], margin=0.0124), lcb:conservative
- seller_self_bid | first_place | h=10 | kingmaker -> mean:conservative (first_place_rate=0.4571, ci95=[0.4238,0.4903], margin=0.0085), lcb:meta_switch_soft
- seller_self_bid | first_place | h=10 | none -> mean:conservative (first_place_rate=0.5242, ci95=[0.4729,0.5756], margin=0.0875), lcb:conservative
- seller_self_bid | first_place | h=10 | respect -> mean:conservative (first_place_rate=0.4884, ci95=[0.4486,0.5282], margin=0.0466), lcb:conservative
- seller_self_bid | robustness | h=10 | herd -> mean:meta_switch (robustness=122.7471, ci95=[98.0184,147.4758], margin=11.8598), lcb:meta_switch
- seller_self_bid | robustness | h=10 | kingmaker -> mean:meta_switch_soft (robustness=89.0767, ci95=[70.3561,107.7973], margin=2.6885), lcb:conservative
- seller_self_bid | robustness | h=10 | none -> mean:meta_switch (robustness=138.7441, ci95=[123.3396,154.1486], margin=11.8148), lcb:meta_switch
- seller_self_bid | robustness | h=10 | respect -> mean:meta_switch (robustness=120.0158, ci95=[106.3765,133.6550], margin=16.6392), lcb:meta_switch
- single_card_sell | ev | h=10 | herd -> mean:conservative (expected_pnl=152.8771, ci95=[147.5432,158.2110], margin=12.9718), lcb:conservative
- single_card_sell | ev | h=10 | kingmaker -> mean:conservative (expected_pnl=144.4053, ci95=[134.3372,154.4733], margin=10.9531), lcb:conservative
- single_card_sell | ev | h=10 | none -> mean:conservative (expected_pnl=178.8412, ci95=[162.9153,194.7671], margin=19.5293), lcb:conservative
- single_card_sell | ev | h=10 | respect -> mean:conservative (expected_pnl=153.8989, ci95=[141.8067,165.9912], margin=1.4101), lcb:meta_switch_soft
- single_card_sell | first_place | h=10 | herd -> mean:conservative (first_place_rate=0.4495, ci95=[0.4281,0.4708], margin=0.0136), lcb:conservative
- single_card_sell | first_place | h=10 | kingmaker -> mean:meta_switch_soft (first_place_rate=0.4474, ci95=[0.4240,0.4708], margin=0.0251), lcb:meta_switch_soft
- single_card_sell | first_place | h=10 | none -> mean:meta_switch_soft (first_place_rate=0.4772, ci95=[0.4243,0.5301], margin=0.0236), lcb:conservative
- single_card_sell | first_place | h=10 | respect -> mean:conservative (first_place_rate=0.4780, ci95=[0.4471,0.5090], margin=0.0156), lcb:meta_switch_soft
- single_card_sell | robustness | h=10 | herd -> mean:conservative (robustness=138.7604, ci95=[119.3604,158.1605], margin=17.3223), lcb:conservative
- single_card_sell | robustness | h=10 | kingmaker -> mean:meta_switch_soft (robustness=99.5215, ci95=[87.1466,111.8964], margin=18.6973), lcb:meta_switch_soft
- single_card_sell | robustness | h=10 | none -> mean:meta_switch (robustness=121.0878, ci95=[82.4044,159.7711], margin=6.9166), lcb:conservative
- single_card_sell | robustness | h=10 | respect -> mean:meta_switch (robustness=114.2231, ci95=[83.6104,144.8358], margin=2.3135), lcb:conservative
- standard_rankings | ev | h=10 | herd -> mean:conservative (expected_pnl=164.3498, ci95=[152.4542,176.2453], margin=38.2298), lcb:conservative
- standard_rankings | ev | h=10 | kingmaker -> mean:conservative (expected_pnl=125.3920, ci95=[115.2602,135.5239], margin=8.6102), lcb:conservative
- standard_rankings | ev | h=10 | none -> mean:conservative (expected_pnl=181.4496, ci95=[169.0952,193.8039], margin=38.7515), lcb:conservative
- standard_rankings | ev | h=10 | respect -> mean:conservative (expected_pnl=152.2182, ci95=[141.2252,163.2113], margin=19.7574), lcb:conservative
- standard_rankings | first_place | h=10 | herd -> mean:conservative (first_place_rate=0.5066, ci95=[0.4551,0.5580], margin=0.0898), lcb:conservative
- standard_rankings | first_place | h=10 | kingmaker -> mean:conservative (first_place_rate=0.4306, ci95=[0.3913,0.4700], margin=0.0179), lcb:meta_switch_soft
- standard_rankings | first_place | h=10 | none -> mean:conservative (first_place_rate=0.5443, ci95=[0.5071,0.5815], margin=0.0729), lcb:conservative
- standard_rankings | first_place | h=10 | respect -> mean:conservative (first_place_rate=0.5186, ci95=[0.4562,0.5810], margin=0.1090), lcb:conservative
- standard_rankings | robustness | h=10 | herd -> mean:meta_switch_soft (robustness=105.0515, ci95=[78.0562,132.0467], margin=20.0594), lcb:meta_switch_soft
- standard_rankings | robustness | h=10 | kingmaker -> mean:meta_switch (robustness=96.7605, ci95=[88.9880,104.5331], margin=26.7530), lcb:meta_switch
- standard_rankings | robustness | h=10 | none -> mean:meta_switch (robustness=113.1659, ci95=[93.0328,133.2990], margin=16.0150), lcb:meta_switch
- standard_rankings | robustness | h=10 | respect -> mean:meta_switch (robustness=99.6459, ci95=[82.1578,117.1341], margin=1.9432), lcb:meta_switch

from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.706,
        delta_scale=6997.8,
        min_delta=684,
        max_stack_frac=0.153,
        max_pot_frac=0.241,
        house_multiplier=1.276,
        preserve_weight=0.836,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_007",
    )

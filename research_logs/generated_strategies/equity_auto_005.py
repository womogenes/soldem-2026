from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.845,
        delta_scale=6850.4,
        min_delta=401,
        max_stack_frac=0.202,
        max_pot_frac=0.2,
        house_multiplier=1.15,
        preserve_weight=0.889,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_005",
    )

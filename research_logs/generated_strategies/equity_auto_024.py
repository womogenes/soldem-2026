from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=1.02,
        delta_scale=6986.7,
        min_delta=608,
        max_stack_frac=0.253,
        max_pot_frac=0.123,
        house_multiplier=1.185,
        preserve_weight=1.325,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_024",
    )

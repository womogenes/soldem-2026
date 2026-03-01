from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.765,
        delta_scale=5890.5,
        min_delta=426,
        max_stack_frac=0.206,
        max_pot_frac=0.181,
        house_multiplier=1.052,
        preserve_weight=1.114,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_011",
    )

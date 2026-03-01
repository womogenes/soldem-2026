from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.783,
        delta_scale=6189.6,
        min_delta=305,
        max_stack_frac=0.227,
        max_pot_frac=0.128,
        house_multiplier=1.285,
        preserve_weight=0.788,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_028",
    )

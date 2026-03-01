from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.729,
        delta_scale=7030.7,
        min_delta=1037,
        max_stack_frac=0.237,
        max_pot_frac=0.253,
        house_multiplier=1.417,
        preserve_weight=0.843,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_030",
    )

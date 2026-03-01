from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.857,
        delta_scale=6284.0,
        min_delta=267,
        max_stack_frac=0.31,
        max_pot_frac=0.254,
        house_multiplier=1.142,
        preserve_weight=0.896,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_009",
    )

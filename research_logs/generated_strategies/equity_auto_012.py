from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.692,
        delta_scale=7470.5,
        min_delta=1036,
        max_stack_frac=0.278,
        max_pot_frac=0.176,
        house_multiplier=1.274,
        preserve_weight=1.086,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_012",
    )

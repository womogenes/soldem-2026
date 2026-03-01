from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.814,
        delta_scale=7149.2,
        min_delta=737,
        max_stack_frac=0.278,
        max_pot_frac=0.156,
        house_multiplier=1.378,
        preserve_weight=0.895,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_025",
    )

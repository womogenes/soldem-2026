from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.849,
        delta_scale=7522.2,
        min_delta=804,
        max_stack_frac=0.28,
        max_pot_frac=0.226,
        house_multiplier=1.293,
        preserve_weight=0.921,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_004",
    )

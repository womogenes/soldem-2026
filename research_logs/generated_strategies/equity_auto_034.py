from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.694,
        delta_scale=5454.5,
        min_delta=317,
        max_stack_frac=0.228,
        max_pot_frac=0.114,
        house_multiplier=1.359,
        preserve_weight=1.251,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_034",
    )

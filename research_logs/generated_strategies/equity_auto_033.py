from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.783,
        delta_scale=6477.5,
        min_delta=681,
        max_stack_frac=0.194,
        max_pot_frac=0.206,
        house_multiplier=1.289,
        preserve_weight=1.002,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_033",
    )

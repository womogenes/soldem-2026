from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.952,
        delta_scale=6172.4,
        min_delta=447,
        max_stack_frac=0.188,
        max_pot_frac=0.194,
        house_multiplier=1.075,
        preserve_weight=0.655,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_010",
    )

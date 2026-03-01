from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.725,
        delta_scale=7000.0,
        min_delta=827,
        max_stack_frac=0.204,
        max_pot_frac=0.108,
        house_multiplier=1.359,
        preserve_weight=1.023,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_016",
    )

from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.642,
        delta_scale=5719.3,
        min_delta=578,
        max_stack_frac=0.303,
        max_pot_frac=0.183,
        house_multiplier=1.233,
        preserve_weight=0.801,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_002",
    )

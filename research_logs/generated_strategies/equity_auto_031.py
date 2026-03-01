from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.758,
        delta_scale=6997.3,
        min_delta=1074,
        max_stack_frac=0.321,
        max_pot_frac=0.195,
        house_multiplier=1.411,
        preserve_weight=0.854,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_031",
    )

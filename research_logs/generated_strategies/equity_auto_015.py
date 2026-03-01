from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=1.04,
        delta_scale=6474.6,
        min_delta=717,
        max_stack_frac=0.325,
        max_pot_frac=0.181,
        house_multiplier=1.238,
        preserve_weight=1.147,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_015",
    )

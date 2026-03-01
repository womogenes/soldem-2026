from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.902,
        delta_scale=6592.6,
        min_delta=895,
        max_stack_frac=0.228,
        max_pot_frac=0.176,
        house_multiplier=1.319,
        preserve_weight=1.323,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_003",
    )

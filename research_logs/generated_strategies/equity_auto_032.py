from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.852,
        delta_scale=6385.7,
        min_delta=751,
        max_stack_frac=0.235,
        max_pot_frac=0.117,
        house_multiplier=1.235,
        preserve_weight=1.106,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_032",
    )

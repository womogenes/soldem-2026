from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.999,
        delta_scale=7230.4,
        min_delta=622,
        max_stack_frac=0.182,
        max_pot_frac=0.255,
        house_multiplier=1.287,
        preserve_weight=0.898,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_018",
    )

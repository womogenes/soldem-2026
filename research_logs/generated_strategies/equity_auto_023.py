from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.984,
        delta_scale=6057.7,
        min_delta=781,
        max_stack_frac=0.265,
        max_pot_frac=0.106,
        house_multiplier=1.303,
        preserve_weight=1.245,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_023",
    )

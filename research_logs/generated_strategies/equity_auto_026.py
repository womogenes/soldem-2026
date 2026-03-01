from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.887,
        delta_scale=5735.8,
        min_delta=274,
        max_stack_frac=0.227,
        max_pot_frac=0.208,
        house_multiplier=0.968,
        preserve_weight=1.063,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_026",
    )

from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.704,
        delta_scale=5645.2,
        min_delta=252,
        max_stack_frac=0.266,
        max_pot_frac=0.147,
        house_multiplier=1.151,
        preserve_weight=0.934,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_000",
    )

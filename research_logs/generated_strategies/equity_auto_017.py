from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.936,
        delta_scale=6602.8,
        min_delta=589,
        max_stack_frac=0.211,
        max_pot_frac=0.132,
        house_multiplier=1.152,
        preserve_weight=0.906,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_017",
    )

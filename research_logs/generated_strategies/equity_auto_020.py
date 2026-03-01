from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.9,
        delta_scale=6604.4,
        min_delta=529,
        max_stack_frac=0.224,
        max_pot_frac=0.178,
        house_multiplier=0.995,
        preserve_weight=1.163,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_020",
    )

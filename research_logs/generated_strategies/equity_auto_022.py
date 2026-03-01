from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.651,
        delta_scale=7522.5,
        min_delta=868,
        max_stack_frac=0.309,
        max_pot_frac=0.207,
        house_multiplier=1.383,
        preserve_weight=1.244,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_022",
    )

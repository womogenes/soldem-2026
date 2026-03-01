from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=1.013,
        delta_scale=5419.2,
        min_delta=675,
        max_stack_frac=0.214,
        max_pot_frac=0.246,
        house_multiplier=1.388,
        preserve_weight=0.94,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_035",
    )

from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=1.044,
        delta_scale=6920.4,
        min_delta=407,
        max_stack_frac=0.218,
        max_pot_frac=0.212,
        house_multiplier=0.958,
        preserve_weight=1.127,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_021",
    )

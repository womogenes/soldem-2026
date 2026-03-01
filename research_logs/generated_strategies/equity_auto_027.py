from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.829,
        delta_scale=7055.2,
        min_delta=456,
        max_stack_frac=0.177,
        max_pot_frac=0.165,
        house_multiplier=1.27,
        preserve_weight=1.141,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_027",
    )

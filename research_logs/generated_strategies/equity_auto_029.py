from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.807,
        delta_scale=7187.3,
        min_delta=345,
        max_stack_frac=0.315,
        max_pot_frac=0.242,
        house_multiplier=0.981,
        preserve_weight=0.902,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_029",
    )

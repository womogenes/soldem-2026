from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.869,
        delta_scale=7524.4,
        min_delta=1089,
        max_stack_frac=0.219,
        max_pot_frac=0.229,
        house_multiplier=1.12,
        preserve_weight=0.891,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_014",
    )

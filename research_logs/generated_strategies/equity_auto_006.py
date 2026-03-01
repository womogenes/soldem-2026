from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.978,
        delta_scale=6014.4,
        min_delta=300,
        max_stack_frac=0.303,
        max_pot_frac=0.244,
        house_multiplier=1.332,
        preserve_weight=1.066,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_006",
    )

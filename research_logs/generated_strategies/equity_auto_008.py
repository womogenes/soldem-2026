from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.672,
        delta_scale=6730.3,
        min_delta=485,
        max_stack_frac=0.294,
        max_pot_frac=0.155,
        house_multiplier=1.172,
        preserve_weight=0.858,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_008",
    )

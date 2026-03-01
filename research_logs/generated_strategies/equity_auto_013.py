from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.698,
        delta_scale=7172.3,
        min_delta=438,
        max_stack_frac=0.317,
        max_pot_frac=0.24,
        house_multiplier=1.274,
        preserve_weight=1.037,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_013",
    )

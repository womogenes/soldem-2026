from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.645,
        delta_scale=6781.5,
        min_delta=383,
        max_stack_frac=0.162,
        max_pot_frac=0.139,
        house_multiplier=0.964,
        preserve_weight=0.817,
        sell_count_early=2,
        sell_count_late=1,
        tag="equity_auto_001",
    )

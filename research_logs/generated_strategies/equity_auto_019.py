from strategies.builtin import EquityAwareStrategy


def build():
    return EquityAwareStrategy(
        bid_multiplier=0.929,
        delta_scale=5596.8,
        min_delta=656,
        max_stack_frac=0.256,
        max_pot_frac=0.227,
        house_multiplier=1.324,
        preserve_weight=1.271,
        sell_count_early=1,
        sell_count_late=1,
        tag="equity_auto_019",
    )

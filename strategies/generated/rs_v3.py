from strategies.builtin import RegimeSwitchStrategy

def build():
    return RegimeSwitchStrategy(
        reserve_base=0.115,
        reserve_min=0.075,
        reserve_max=0.175,
        eq_samples=14,
        jitter=0.08,
        tag='rs_v3',
    )

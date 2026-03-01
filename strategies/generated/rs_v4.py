from strategies.builtin import RegimeSwitchStrategy

def build():
    return RegimeSwitchStrategy(
        reserve_base=0.100,
        reserve_min=0.065,
        reserve_max=0.145,
        eq_samples=18,
        jitter=0.04,
        tag='rs_v4',
    )

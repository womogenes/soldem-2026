from strategies.builtin import RegimeSwitchStrategy

def build():
    return RegimeSwitchStrategy(
        reserve_base=0.105,
        reserve_min=0.070,
        reserve_max=0.165,
        eq_samples=16,
        jitter=0.05,
        tag='rs_v2',
    )

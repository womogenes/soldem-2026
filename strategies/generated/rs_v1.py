from strategies.builtin import RegimeSwitchStrategy

def build():
    return RegimeSwitchStrategy(
        reserve_base=0.095,
        reserve_min=0.070,
        reserve_max=0.155,
        eq_samples=14,
        jitter=0.06,
        tag='rs_v1',
    )

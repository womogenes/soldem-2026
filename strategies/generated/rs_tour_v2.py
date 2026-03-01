from strategies.builtin import RegimeSwitchStrategy


def build():
    return RegimeSwitchStrategy(
        reserve_base=0.090,
        reserve_min=0.055,
        reserve_max=0.150,
        eq_samples=24,
        jitter=0.03,
        tag='rs_tour_v2',
    )

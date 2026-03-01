from strategies.builtin import RegimeSwitchStrategy


def build():
    return RegimeSwitchStrategy(
        reserve_base=0.110,
        reserve_min=0.070,
        reserve_max=0.170,
        eq_samples=20,
        jitter=0.02,
        tag='rs_tour_v3',
    )

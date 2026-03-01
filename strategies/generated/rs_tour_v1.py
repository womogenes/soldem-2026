from strategies.builtin import RegimeSwitchStrategy


def build():
    return RegimeSwitchStrategy(
        reserve_base=0.095,
        reserve_min=0.060,
        reserve_max=0.160,
        eq_samples=18,
        jitter=0.04,
        tag='rs_tour_v1',
    )

from strategies.builtin import MarketMakerStrategy


def build():
    return MarketMakerStrategy(reserve_frac=0.070, tag='mm_r0070')

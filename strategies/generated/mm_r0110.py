from strategies.builtin import MarketMakerStrategy

def build():
    return MarketMakerStrategy(reserve_frac=0.110, tag='mm_r0110')

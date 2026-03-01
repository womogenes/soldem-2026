from strategies.builtin import MarketMakerStrategy

def build():
    return MarketMakerStrategy(reserve_frac=0.090, tag='mm_r0090')

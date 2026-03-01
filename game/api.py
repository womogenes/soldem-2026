from typing import Literal
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from game.engine_base import Game, N_PLAYERS

Phase = Literal["idle", "sell", "bid", "choose", "showdown"]


class SellReq(BaseModel):
    indices: list[int]


class BidReq(BaseModel):
    amount: int


class ChooseReq(BaseModel):
    index: int


class Session:
    def __init__(self):
        self.match_pnl = [0] * N_PLAYERS
        self.round_winner = -1
        self.phase: Phase = "idle"
        self.action = "Start new game"
        self.log: list[str] = []
        self.game = Game(ante_amt=40, n_orbits=3)

    def _bot_sell_cards(self, cards):
        return [cards[random.randint(0, len(cards) - 1)]]

    def _bot_bid(self, idx: int) -> int:
        max_bid = min(self.game.player_stacks[idx], max(0, self.game.pot // 4))
        return random.randint(0, max_bid)

    def _state(self):
        return {
            "phase": self.phase,
            "action": self.action,
            "round_winner": self.round_winner,
            "match_pnl": self.match_pnl,
            "log": self.log,
            "pot": self.game.pot,
            "round_num": self.game.round_num,
            "n_orbits": self.game.n_orbits,
            "seller_idx": self.game.seller_idx,
            "player_cards": self.game.player_cards,
            "player_stacks": self.game.player_stacks,
            "auc_cards": self.game.auc_cards,
        }

    def new_game(self):
        self.match_pnl = [0] * N_PLAYERS
        self.log = []
        return self.reset_game()

    def reset_game(self):
        self.game = Game(ante_amt=40, n_orbits=3)
        self.game.reset()
        self.log = []
        self.round_winner = -1
        self.phase = "bid"
        self.action = "Bid for house card"
        self.log.append(f"House auctions {self._card_text(self.game.auc_cards[0])}")
        return self._state()

    def _card_text(self, card):
        suit = {
            "C": "clubs",
            "D": "diamonds",
            "H": "hearts",
            "S": "spades",
            "X": "citadel",
        }[card[1]]
        return f"{card[0]} of {suit}"

    def _seller_text(self):
        if self.game.seller_idx == -1:
            return "House"
        return f"Player {self.game.seller_idx}"

    def _finish_auction(self, chosen):
        winner = self.game.last_winner_idx
        self.log.append(
            f"Player {winner} wins {self._card_text(chosen)} from {self._seller_text()}"
        )
        out = self.game.win_card(chosen)
        if out["game_over"]:
            self.round_winner = out["winner_idx"]
            self.game.player_stacks[self.round_winner] += self.game.pot
            self.game.pot = 0
            for i in range(N_PLAYERS):
                self.match_pnl[i] += self.game.player_stacks[i] - self.game.start_chips
            self.log.append(f"Showdown winner: Player {self.round_winner}")
            self.phase = "showdown"
            self.action = "Round over"
            return self._state()

        if self.game.seller_idx == 0:
            self.game.auc_cards = []
            self.phase = "sell"
            self.action = "Choose cards to sell"
            return self._state()

        self.game.auc_cards = self._bot_sell_cards(self.game.player_cards[self.game.seller_idx])
        self.log.append(
            f"Player {self.game.seller_idx} auctions {self._card_text(self.game.auc_cards[0])}"
        )
        self.phase = "bid"
        self.action = f"Bid for P{self.game.seller_idx} card"
        return self._state()

    def sell(self, indices: list[int]):
        picks = indices if indices else [0]
        self.game.auc_cards = [self.game.player_cards[0][i] for i in picks]
        for card in self.game.auc_cards:
            self.log.append(f"Player 0 auctions {self._card_text(card)}")
        self.phase = "bid"
        self.action = "Bid for your auction"
        return self._state()

    def bid(self, amount: int):
        self.game.player_bids = [None] * N_PLAYERS
        for i in range(N_PLAYERS):
            if i == self.game.seller_idx:
                continue
            if i == 0:
                self.game.player_bid(0, amount)
            else:
                self.game.player_bid(i, self._bot_bid(i))
        res = self.game.close_bids()
        self.log.append(
            f"Bid winner: Player {res['winner']} for {res['bid_price']}"
        )
        if res["winner"] == 0:
            self.phase = "choose"
            self.action = "Choose won card"
            return self._state()
        return self._finish_auction(self.game.auc_cards[0])

    def choose(self, index: int):
        return self._finish_auction(self.game.auc_cards[index])


session = Session()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/state")
def state():
    return session._state()


@app.post("/new_game")
def new_game():
    return session.new_game()


@app.post("/reset_game")
def reset_game():
    return session.reset_game()


@app.post("/sell")
def sell(req: SellReq):
    return session.sell(req.indices)


@app.post("/bid")
def bid(req: BidReq):
    return session.bid(req.amount)


@app.post("/choose")
def choose(req: ChooseReq):
    return session.choose(req.index)

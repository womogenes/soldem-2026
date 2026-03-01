from itertools import product
import random
import copy
import time
from utils import compare_hands

N_PLAYERS = 5
N_PLAYER_CARDS = 5

# Hard-coded for now
BASE_DECK = list(product(range(1, 11), "CDHSX"))

class Game:
    def __init__(
        self,
        start_chips=200,
        ante_amt=200,
        n_orbits=3,
    ):
        """
        Create a new game. To reset a game, make a new one.
        """
        self.start_chips = start_chips
        self.ante_amt = ante_amt
        self.n_orbits = n_orbits

        self.player_stacks = [start_chips] * N_PLAYERS

        # Deal
        self.player_cards = [[] for _ in range(N_PLAYERS)]

        # state is an int (round number)
        self.round_num = None
        self.seller_idx = None
        self.player_bids = [None] * N_PLAYERS

        # Central cards?
        self.auc_cards = []
        self.pot = 0
        self.last_winner_idx = None
        self.last_win_amt = 0
        self.turns_in_orbit = 0

    def reset(self):
        """
        Reset the game. Return cards as list of tuples.
        """
        # Deal cards
        deck = copy.deepcopy(BASE_DECK)
        random.shuffle(deck)
        for i in range(N_PLAYERS):
            self.player_cards[i] = deck[:N_PLAYER_CARDS]
            deck = deck[N_PLAYER_CARDS:]
        
        # Take antes. Stacks reset at the start of each round.
        self.player_stacks = [self.start_chips - self.ante_amt] * N_PLAYERS
        self.pot = self.ante_amt * N_PLAYERS
        
        # House puts down a card. Reset bids
        self.auc_cards = [deck.pop(0)]
        self.player_bids = [None] * N_PLAYERS
        self.last_winner_idx = None
        self.last_win_amt = 0
        self.turns_in_orbit = 0

        # Set round number
        self.round_num = 0
        self.seller_idx = -1    # House
        return {
            "game_over": False,
            "seller_idx": self.seller_idx,
            "round_num": self.round_num,
            "player_cards": copy.deepcopy(self.player_cards),
            "player_stacks": list(self.player_stacks),
            "pot": self.pot,
            "auc_cards": list(self.auc_cards),
        }

    def player_bid(self, player_idx: int, amt: int):
        """
        Set player bid amount.
        """
        amt = min(self.player_stacks[player_idx], amt)
        self.player_bids[player_idx] = (amt, time.time())

    def close_bids(self):
        """
        Close bidding and determine who bid the most.
        Update stacks. House auction goes to pot.
        Winner must select card.
        Return as tuple winner, amt, available cards, and new stacks.
        """
        valid = [
            (idx, bid[0], bid[1])
            for idx, bid in enumerate(self.player_bids)
            if bid is not None
        ]
        winner_idx, amt, _ = max(valid, key=lambda x: (x[1], -x[2]))
        self.last_winner_idx = winner_idx
        self.last_win_amt = amt

        if self.seller_idx == -1:
            self.player_stacks[winner_idx] -= amt
            self.pot += amt
        else:
            self.player_stacks[winner_idx] -= amt
            self.player_stacks[self.seller_idx] += amt

        return {
            "winner": winner_idx,
            "bid_price": amt,
            "won_cards": list(self.auc_cards),
            "player_stacks": list(self.player_stacks),
        }

    def win_card(self, card_choice=None):
        """
        Must be called after close_bids. Winner chooses what card they want.
        Update hands. Return new hands and updated state.
        """
        if card_choice is None:
            chosen = self.auc_cards[0]
        elif isinstance(card_choice, int):
            chosen = self.auc_cards[card_choice]
        else:
            chosen = card_choice

        winner_idx = self.last_winner_idx
        self.player_cards[winner_idx].append(chosen)

        if self.seller_idx >= 0 and chosen in self.player_cards[self.seller_idx]:
            self.player_cards[self.seller_idx].remove(chosen)

        if self.seller_idx == -1:
            self.seller_idx = winner_idx
        else:
            self.turns_in_orbit += 1
            if self.turns_in_orbit == N_PLAYERS:
                self.round_num += 1
                self.turns_in_orbit = 0
            self.seller_idx = (self.seller_idx + 1) % N_PLAYERS

        # If game end, declare winner.
        if self.round_num >= self.n_orbits:
            winner = 0
            for i in range(1, N_PLAYERS):
                if compare_hands(self.player_cards[i], self.player_cards[winner]) > 0:
                    winner = i
                
            return {
                "game_over": True,
                "winner_idx": winner,
                "player_cards": copy.deepcopy(self.player_cards),
                "player_stacks": list(self.player_stacks),
                "pot": self.pot,
            }

        self.auc_cards = list(self.player_cards[self.seller_idx])
        self.player_bids = [None] * N_PLAYERS

        return {
            "game_over": False,
            "seller_idx": self.seller_idx,
            "round_num": self.round_num,
            "player_cards": copy.deepcopy(self.player_cards),
            "player_stacks": list(self.player_stacks),
            "pot": self.pot,
            "auc_cards": list(self.auc_cards),
        }

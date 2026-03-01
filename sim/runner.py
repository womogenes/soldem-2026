from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from game.engine_base import Game
from game.rules import resolve_profile
from sim.metrics import composite_profiles, composite_score, first_place_rate, robustness_score
from sim.opponent_models import CorrelationModel, adjust_bid
from strategies import PlayerProfile, StrategyContext
from strategies.loader import load_strategy


@dataclass
class MatchConfig:
    n_games: int = 10
    seed: int = 0
    rule_profile: str = "baseline_v1"
    rule_overrides: dict[str, Any] | None = None
    objective: str = "ev"


class MatchRunner:
    def __init__(self, strategy_specs: list[str], config: MatchConfig):
        self.profile = resolve_profile(config.rule_profile, **(config.rule_overrides or {}))
        self.n_players = int(self.profile.n_players)
        if len(strategy_specs) != self.n_players:
            raise ValueError(
                f"Exactly {self.n_players} strategy tags are required for one table"
            )
        self.strategy_specs = list(strategy_specs)
        self.config = config
        self.strategies = [load_strategy(spec) for spec in strategy_specs]
        self.strategy_tags = [
            getattr(strategy, "tag", spec)
            for strategy, spec in zip(self.strategies, self.strategy_specs)
        ]
        self.rng = random.Random(config.seed)

    def _ctx(
        self,
        game: Game,
        seat: int,
        profiles: dict[int, PlayerProfile],
        objective: str,
    ) -> StrategyContext:
        return StrategyContext(
            seat=seat,
            seller_idx=game.seller_idx if game.seller_idx is not None else -1,
            pot=game.pot,
            round_num=game.round_num if game.round_num is not None else 0,
            n_orbits=game.n_orbits,
            stacks=list(game.player_stacks),
            my_cards=list(game.player_cards[seat]),
            auction_cards=list(game.auc_cards),
            ranking_policy=game.rules.hand_ranking_policy,
            objective=objective,
            player_profiles=profiles,
        )

    def run(
        self,
        correlation: CorrelationModel | None = None,
        compact_log_path: str | None = None,
    ) -> dict:
        correlation = correlation or CorrelationModel()
        profiles = {i: PlayerProfile(seat=i) for i in range(self.n_players)}
        seat_total_pnl = [0] * self.n_players
        seat_firsts = [0] * self.n_players
        game_rows: list[dict] = []

        log_file = None
        if compact_log_path:
            Path(compact_log_path).parent.mkdir(parents=True, exist_ok=True)
            log_file = open(compact_log_path, "a", encoding="utf-8")

        try:
            for gix in range(self.config.n_games):
                game_seed = self.rng.randint(0, 2**31 - 1)
                game = Game(rule_profile=self.profile)
                game.reset(seed=game_seed)

                for seat, strategy in enumerate(self.strategies):
                    strategy.on_round_start(
                        self._ctx(game, seat, profiles, self.config.objective)
                    )

                while True:
                    seller = game.seller_idx
                    if seller is None:
                        raise RuntimeError("Seller index unexpectedly None")

                    if seller >= 0:
                        sell_ctx = self._ctx(game, seller, profiles, self.config.objective)
                        sell_indices = self.strategies[seller].choose_sell_indices(sell_ctx)
                        game.prepare_auction(card_indices=sell_indices)

                    raw_bids: dict[int, int] = {}
                    for bidder in game.eligible_bidders():
                        bid_ctx = self._ctx(game, bidder, profiles, self.config.objective)
                        raw_bid = self.strategies[bidder].bid_amount(bid_ctx)
                        adj_bid = adjust_bid(
                            bidder,
                            seller,
                            raw_bid,
                            raw_bids,
                            game.player_stacks,
                            correlation,
                            self.rng,
                        )
                        raw_bids[bidder] = adj_bid
                        game.player_bid(
                            bidder,
                            adj_bid,
                            bid_ts=(gix * 1000.0) + bidder + (0.01 * len(raw_bids)),
                        )

                        prof = profiles[bidder]
                        prof.bid_count += 1
                        prof.avg_bid += (adj_bid - prof.avg_bid) / prof.bid_count
                        stack_ref = max(1, game.start_chips)
                        prof.aggression += ((adj_bid / stack_ref) - prof.aggression) / prof.bid_count

                    close = game.close_bids()
                    winner = close["winner"]
                    choose_ctx = self._ctx(game, winner, profiles, self.config.objective)
                    chosen_idx = self.strategies[winner].choose_won_card(choose_ctx)
                    chosen_idx = max(0, min(chosen_idx, len(game.auc_cards) - 1))
                    out = game.win_card(chosen_idx)

                    if out["game_over"]:
                        stacks = out["player_stacks"]
                        pnl = [s - game.start_chips for s in stacks]
                        for i in range(self.n_players):
                            seat_total_pnl[i] += pnl[i]

                        ranked = sorted(
                            range(self.n_players),
                            key=lambda i: (pnl[i], stacks[i]),
                            reverse=True,
                        )
                        rank_pos = [0] * self.n_players
                        for pos, seat in enumerate(ranked, start=1):
                            rank_pos[seat] = pos
                        for i in range(self.n_players):
                            if rank_pos[i] == 1:
                                seat_firsts[i] += 1

                        row = {
                            "g": gix,
                            "sd": game_seed,
                            "pnl": pnl,
                            "rk": rank_pos,
                            "w": out.get("winner_idxs", [out.get("winner_idx", 0)]),
                            "pp": out.get("payouts", [0] * self.n_players),
                        }
                        game_rows.append(row)
                        if log_file:
                            log_file.write(json.dumps(row, separators=(",", ":")) + "\n")
                        break

            seat_avg_pnl = [x / self.config.n_games for x in seat_total_pnl]
            seat_first_rate = [x / self.config.n_games for x in seat_firsts]
            return {
                "strategy_tags": list(self.strategy_tags),
                "n_games": self.config.n_games,
                "seed": self.config.seed,
                "rule_profile": self.profile.to_dict(),
                "seat_avg_pnl": seat_avg_pnl,
                "seat_first_rate": seat_first_rate,
                "games": game_rows,
            }
        finally:
            if log_file:
                log_file.close()


def run_match(
    strategy_tags: list[str],
    n_games: int = 10,
    seed: int = 0,
    rule_profile: str = "baseline_v1",
    rule_overrides: dict[str, Any] | None = None,
    objective: str = "ev",
    correlation: CorrelationModel | None = None,
    compact_log_path: str | None = None,
) -> dict:
    config = MatchConfig(
        n_games=n_games,
        seed=seed,
        rule_profile=rule_profile,
        rule_overrides=rule_overrides,
        objective=objective,
    )
    runner = MatchRunner(strategy_tags, config)
    return runner.run(correlation=correlation, compact_log_path=compact_log_path)


def run_population_tournament(
    strategy_tags: list[str],
    n_matches: int = 100,
    n_games_per_match: int = 10,
    rule_profile: str = "baseline_v1",
    rule_overrides: dict[str, Any] | None = None,
    seed: int = 0,
    objective: str = "ev",
    correlation: CorrelationModel | None = None,
) -> dict:
    rng = random.Random(seed)
    profile = resolve_profile(rule_profile, **(rule_overrides or {}))
    n_players = int(profile.n_players)
    per_tag_pnl: dict[str, list[float]] = defaultdict(list)
    per_tag_rankpos: dict[str, list[int]] = defaultdict(list)

    for mix in range(n_matches):
        if len(strategy_tags) >= n_players:
            seats = rng.sample(strategy_tags, n_players)
        else:
            seats = [rng.choice(strategy_tags) for _ in range(n_players)]
        out = run_match(
            seats,
            n_games=n_games_per_match,
            seed=rng.randint(0, 2**31 - 1),
            rule_profile=rule_profile,
            rule_overrides=rule_overrides,
            objective=objective,
            correlation=correlation,
        )

        for g in out["games"]:
            for seat, tag in enumerate(out["strategy_tags"]):
                per_tag_pnl[tag].append(g["pnl"][seat])
                per_tag_rankpos[tag].append(g["rk"][seat])

    profiles = composite_profiles()
    leaderboard: list[dict] = []
    for tag in sorted(per_tag_pnl):
        pnl = per_tag_pnl[tag]
        rpos = per_tag_rankpos[tag]
        ev = mean(pnl) if pnl else 0.0
        first = first_place_rate(rpos)
        robust = robustness_score(pnl)
        scores = {
            name: composite_score(ev, first, robust, weights)
            for name, weights in profiles.items()
        }
        leaderboard.append(
            {
                "tag": tag,
                "samples": len(pnl),
                "expected_pnl": ev,
                "first_place_rate": first,
                "robustness": robust,
                "composites": scores,
            }
        )

    leaderboard.sort(key=lambda row: row["expected_pnl"], reverse=True)
    return {
        "n_matches": n_matches,
        "n_games_per_match": n_games_per_match,
        "rule_profile": rule_profile,
        "rule_overrides": rule_overrides or {},
        "objective": objective,
        "leaderboard": leaderboard,
    }

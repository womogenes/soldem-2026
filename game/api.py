from __future__ import annotations

import time
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from game.advisor import recommend_action
from game.rules import RuleProfile, resolve_profile
from sim.metrics import composite_profiles
from sim.runner import run_population_tournament
from strategies import PlayerProfile, built_in_strategy_factories

Phase = Literal["sell", "bid", "choose", "showdown"]
OutputMode = Literal["action_first", "top3", "metrics", "all"]
Objective = Literal["ev", "first_place", "robustness"]


class RecommendationReq(BaseModel):
    seat: int = 0
    phase: Phase = "bid"
    seller_idx: int = -1
    round_num: int = 0
    n_orbits: int = 3
    pot: int = 0
    stacks: list[int] = Field(default_factory=lambda: [160, 160, 160, 160, 160])
    my_cards: list[tuple[int, str]] = Field(default_factory=list)
    auction_cards: list[tuple[int, str]] = Field(default_factory=list)
    known_cards: list[tuple[int, str]] = Field(default_factory=list)
    objective: Objective = "ev"
    output_mode: OutputMode = "action_first"
    strategy_tag: str | None = None
    ranking_policy: str | None = None


class SessionEventReq(BaseModel):
    event_type: Literal["bid", "auction_result", "showdown", "note"]
    seat: int | None = None
    seller_idx: int | None = None
    amount: int | None = None
    winner_idx: int | None = None
    note: str | None = None
    ts: float | None = None


class ApplyProfileReq(BaseModel):
    profile_name: str = "baseline_v1"
    overrides: dict[str, Any] = Field(default_factory=dict)


class RecomputeChampionsReq(BaseModel):
    n_matches: int = 90
    n_games_per_match: int = 10
    seed: int = 0


class SetChampionsReq(BaseModel):
    ev: str | None = None
    first_place: str | None = None
    robustness: str | None = None
    lock_manual: bool = True


class Session:
    def __init__(self):
        self.rule_profile: RuleProfile = resolve_profile("baseline_v1")
        self.events: list[dict[str, Any]] = []
        self.player_profiles = {i: PlayerProfile(seat=i) for i in range(5)}
        self.champions = {
            "ev": "conservative_plus",
            "first_place": "equity_evolved_v1",
            "robustness": "conservative_plus",
        }
        self.dynamic_resolution_enabled = True
        self.last_leaderboards: dict[str, list[dict[str, Any]]] = {}
        self.strategy_presets = {
            "balanced_default": "conservative_plus",
            "correlated_table": "equity_evolved_v1",
            "risk_on_soft_table": "pot_fraction",
            "house_control": "house_hammer",
            "evolved_attack": "equity_evolved_v1",
        }

    def reset(self):
        self.events = []
        self.player_profiles = {i: PlayerProfile(seat=i) for i in range(5)}

    def apply_profile(self, profile_name: str, overrides: dict[str, Any]):
        self.rule_profile = resolve_profile(profile_name, **overrides)

    def record_event(self, event: SessionEventReq):
        ts = event.ts if event.ts is not None else time.time()
        row = {
            "event_type": event.event_type,
            "seat": event.seat,
            "seller_idx": event.seller_idx,
            "amount": event.amount,
            "winner_idx": event.winner_idx,
            "note": event.note,
            "ts": ts,
        }
        self.events.append(row)

        if event.event_type == "bid" and event.seat is not None and event.amount is not None:
            profile = self.player_profiles[event.seat]
            profile.bid_count += 1
            profile.avg_bid += (event.amount - profile.avg_bid) / profile.bid_count
            profile.aggression += ((event.amount / 200.0) - profile.aggression) / profile.bid_count

    def state(self) -> dict[str, Any]:
        table_read = self.infer_table_read()
        return {
            "rule_profile": self.rule_profile.to_dict(),
            "champions": self.champions,
            "dynamic_resolution_enabled": self.dynamic_resolution_enabled,
            "resolved_champions": {
                "ev": self.resolve_champion("ev"),
                "first_place": self.resolve_champion("first_place"),
                "robustness": self.resolve_champion("robustness"),
            },
            "table_read": table_read,
            "recommended_preset": self.recommend_preset(table_read),
            "strategy_presets": self.strategy_presets,
            "events_count": len(self.events),
            "recent_events": self.events[-20:],
            "player_profiles": {
                i: {
                    "avg_bid": p.avg_bid,
                    "bid_count": p.bid_count,
                    "aggression": p.aggression,
                }
                for i, p in self.player_profiles.items()
            },
            "composite_profiles": composite_profiles(),
        }

    def infer_table_read(self) -> dict[str, Any]:
        bid_events = [e for e in self.events if e.get("event_type") == "bid"]
        auction_events = [e for e in self.events if e.get("event_type") == "auction_result"]

        bid_amounts = [int(e.get("amount") or 0) for e in bid_events]
        n_bids = len(bid_amounts)
        zero_bid_frac = (sum(1 for x in bid_amounts if x <= 0) / n_bids) if n_bids else 0.0
        avg_bid = (sum(bid_amounts) / n_bids) if n_bids else 0.0

        aggr_values = [p.aggression for p in self.player_profiles.values() if p.bid_count > 0]
        avg_aggr = (sum(aggr_values) / len(aggr_values)) if aggr_values else 0.0

        pair_counts: dict[tuple[int, int], int] = {}
        seller_totals: dict[int, int] = {}
        for e in auction_events:
            seller = e.get("seller_idx")
            winner = e.get("winner_idx")
            if seller is None or winner is None:
                continue
            seller = int(seller)
            winner = int(winner)
            if seller < 0 or winner < 0 or seller == winner:
                continue
            pair_counts[(seller, winner)] = pair_counts.get((seller, winner), 0) + 1
            seller_totals[seller] = seller_totals.get(seller, 0) + 1

        pair_bias = 0.0
        dominant_pair: tuple[int, int] | None = None
        for i in range(self.rule_profile.n_players):
            for j in range(i + 1, self.rule_profile.n_players):
                mutual = pair_counts.get((i, j), 0) + pair_counts.get((j, i), 0)
                total = seller_totals.get(i, 0) + seller_totals.get(j, 0)
                if total <= 0:
                    continue
                share = mutual / total
                if share > pair_bias:
                    pair_bias = share
                    dominant_pair = (i, j)

        mode = "balanced"
        confidence = 0.3
        if len(auction_events) >= 6 and pair_bias >= 0.42:
            mode = "correlated_pair"
            confidence = 0.8
        elif n_bids >= 10 and avg_aggr >= 0.32:
            mode = "aggressive"
            confidence = 0.7
        elif n_bids >= 10 and avg_aggr <= 0.14 and zero_bid_frac >= 0.33:
            mode = "passive"
            confidence = 0.7
        elif n_bids >= 10 and 0.16 <= avg_aggr <= 0.30 and zero_bid_frac <= 0.25:
            mode = "competitive"
            confidence = 0.65
        elif n_bids >= 8:
            confidence = 0.55

        return {
            "mode": mode,
            "confidence": confidence,
            "n_bids": n_bids,
            "avg_bid": avg_bid,
            "avg_aggression": avg_aggr,
            "zero_bid_fraction": zero_bid_frac,
            "n_auction_results": len(auction_events),
            "pair_bias": pair_bias,
            "dominant_pair": dominant_pair,
        }

    def recommend_preset(self, table_read: dict[str, Any] | None = None) -> str:
        read = table_read or self.infer_table_read()
        mode = read.get("mode", "balanced")
        if mode == "correlated_pair":
            return "correlated_table"
        if mode == "passive":
            return "risk_on_soft_table"
        if mode == "competitive":
            return "correlated_table"
        return "balanced_default"

    def resolve_champion(self, objective: str) -> str:
        if not self.dynamic_resolution_enabled:
            return self.champions.get(objective, "conservative_plus")

        # Fast day-of adjustment for known profile deltas from offline simulations.
        table_read = self.infer_table_read()
        mode = table_read.get("mode", "balanced")
        profile_bias_evolved = (
            self.rule_profile.pot_distribution_policy in {"high_low_split", "top2_split"}
            or self.rule_profile.seller_can_bid_own_card
            or self.rule_profile.hand_ranking_policy == "standard_plus_five_kind"
            or not self.rule_profile.allow_multi_card_sell
        )

        if mode == "aggressive":
            return "conservative_plus"
        if objective == "first_place":
            if mode == "passive" and table_read.get("confidence", 0.0) >= 0.7:
                return "pot_fraction"
            return "equity_evolved_v1"
        if mode in {"competitive", "correlated_pair"}:
            return "equity_evolved_v1"
        if profile_bias_evolved:
            return "equity_evolved_v1"
        return "conservative_plus"

    def recompute_champions(self, req: RecomputeChampionsReq) -> dict[str, Any]:
        strategy_tags = list(built_in_strategy_factories().keys())
        leaderboards: dict[str, list[dict[str, Any]]] = {}

        objective_to_key = {
            "ev": "expected_pnl",
            "first_place": "first_place_rate",
            "robustness": "robustness",
        }

        for objective in ["ev", "first_place", "robustness"]:
            out = run_population_tournament(
                strategy_tags,
                n_matches=req.n_matches,
                n_games_per_match=req.n_games_per_match,
                rule_profile=self.rule_profile.name,
                seed=req.seed + (101 * len(leaderboards)),
                objective=objective,
            )
            board = out["leaderboard"]
            key = objective_to_key[objective]
            best = max(board, key=lambda row: row[key])
            self.champions[objective] = best["tag"]
            leaderboards[objective] = board

        self.last_leaderboards = leaderboards
        return {
            "champions": self.champions,
            "leaderboards": leaderboards,
        }

    def set_champions(self, req: SetChampionsReq) -> dict[str, Any]:
        if req.ev:
            self.champions["ev"] = req.ev
        if req.first_place:
            self.champions["first_place"] = req.first_place
        if req.robustness:
            self.champions["robustness"] = req.robustness
        if req.lock_manual:
            self.dynamic_resolution_enabled = False
        return {
            "champions": self.champions,
            "dynamic_resolution_enabled": self.dynamic_resolution_enabled,
            "resolved_champions": {
                "ev": self.resolve_champion("ev"),
                "first_place": self.resolve_champion("first_place"),
                "robustness": self.resolve_champion("robustness"),
            },
        }


session = Session()
app = FastAPI(title="Sold 'Em advisor API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/session/state")
def session_state():
    return session.state()


@app.post("/session/reset")
def session_reset():
    session.reset()
    return session.state()


@app.post("/session/event")
def session_event(req: SessionEventReq):
    session.record_event(req)
    return {"ok": True, "events_count": len(session.events)}


@app.post("/rules/apply_profile")
def rules_apply_profile(req: ApplyProfileReq):
    session.apply_profile(req.profile_name, req.overrides)
    return {"ok": True, "rule_profile": session.rule_profile.to_dict()}


@app.get("/strategies/champions")
def strategies_champions():
    return {
        "champions": session.champions,
        "resolved_champions": {
            "ev": session.resolve_champion("ev"),
            "first_place": session.resolve_champion("first_place"),
            "robustness": session.resolve_champion("robustness"),
        },
        "strategy_presets": session.strategy_presets,
        "composite_profiles": composite_profiles(),
        "leaderboards": session.last_leaderboards,
    }


@app.post("/strategies/recompute_champions")
def strategies_recompute(req: RecomputeChampionsReq):
    return session.recompute_champions(req)


@app.post("/strategies/set_champions")
def strategies_set_champions(req: SetChampionsReq):
    return session.set_champions(req)


@app.post("/advisor/recommend")
def advisor_recommend(req: RecommendationReq):
    ranking_policy = req.ranking_policy or session.rule_profile.hand_ranking_policy
    strategy_tag = req.strategy_tag or session.resolve_champion(req.objective)

    if req.output_mode == "all":
        out = {}
        for mode in ["action_first", "top3", "metrics"]:
            rec = recommend_action(
                phase=req.phase,
                strategy_tag=strategy_tag,
                seat=req.seat,
                seller_idx=req.seller_idx,
                pot=req.pot,
                stacks=req.stacks,
                my_cards=req.my_cards,
                auction_cards=req.auction_cards,
                round_num=req.round_num,
                n_orbits=req.n_orbits,
                ranking_policy=ranking_policy,
                objective=req.objective,
                output_mode=mode,
                player_profiles=session.player_profiles,
                known_cards=req.known_cards,
            )
            out[mode] = rec.to_dict()
        return {
            "strategy_tag": strategy_tag,
            "rule_profile": session.rule_profile.to_dict(),
            "modes": out,
        }

    rec = recommend_action(
        phase=req.phase,
        strategy_tag=strategy_tag,
        seat=req.seat,
        seller_idx=req.seller_idx,
        pot=req.pot,
        stacks=req.stacks,
        my_cards=req.my_cards,
        auction_cards=req.auction_cards,
        round_num=req.round_num,
        n_orbits=req.n_orbits,
        ranking_policy=ranking_policy,
        objective=req.objective,
        output_mode=req.output_mode,
        player_profiles=session.player_profiles,
        known_cards=req.known_cards,
    )
    out = rec.to_dict()
    out["rule_profile"] = session.rule_profile.to_dict()
    return out

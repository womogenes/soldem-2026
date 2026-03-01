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


DISCOVERY_STRATEGY_SPECS = list(built_in_strategy_factories().keys()) + [
    "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2",
    "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2",
    "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1",
    "risk_sniper:bid_scale=0.769,late_round_bonus=0.311,sell_count=2,stack_cap_fraction=0.258,trigger_delta=1600",
]


class Session:
    def __init__(self):
        self.rule_profile: RuleProfile = resolve_profile("baseline_v1")
        self.events: list[dict[str, Any]] = []
        self.player_profiles = {i: PlayerProfile(seat=i) for i in range(5)}
        default_champion = (
            "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2"
        )
        self.champions = {
            "ev": default_champion,
            "first_place": default_champion,
            "robustness": default_champion,
        }
        self.last_leaderboards: dict[str, list[dict[str, Any]]] = {}

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
        return {
            "rule_profile": self.rule_profile.to_dict(),
            "champions": self.champions,
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

    def recompute_champions(self, req: RecomputeChampionsReq) -> dict[str, Any]:
        strategy_tags = list(DISCOVERY_STRATEGY_SPECS)
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
        "composite_profiles": composite_profiles(),
        "leaderboards": session.last_leaderboards,
    }


@app.post("/strategies/recompute_champions")
def strategies_recompute(req: RecomputeChampionsReq):
    return session.recompute_champions(req)


@app.post("/advisor/recommend")
def advisor_recommend(req: RecommendationReq):
    ranking_policy = req.ranking_policy or session.rule_profile.hand_ranking_policy
    strategy_tag = req.strategy_tag or session.champions.get(
        req.objective,
        "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2",
    )

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

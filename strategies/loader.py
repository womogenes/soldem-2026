from __future__ import annotations

import importlib.util
from pathlib import Path

from strategies.builtin import build_strategy, built_in_strategy_factories


def _load_module_from_path(path: Path):
    module_name = f"soldem_strategy_{path.stem}_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load strategy module at {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _coerce_param(raw: str):
    low = raw.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def _parse_builtin_spec(spec: str) -> tuple[str, dict]:
    if ":" not in spec:
        return spec, {}
    tag, param_str = spec.split(":", 1)
    params: dict[str, object] = {}
    for chunk in param_str.split(","):
        part = chunk.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"Invalid strategy parameter fragment: '{part}'")
        k, v = part.split("=", 1)
        params[k.strip()] = _coerce_param(v.strip())
    return tag, params


def _canonical_tag(tag: str, params: dict) -> str:
    if not params:
        return tag
    serialized = ",".join(f"{k}={params[k]}" for k in sorted(params))
    return f"{tag}:{serialized}"


def load_strategy(spec: str):
    tag, params = _parse_builtin_spec(spec)
    factories = built_in_strategy_factories()
    if tag in factories:
        strategy = build_strategy(tag, **params)
        strategy.tag = _canonical_tag(getattr(strategy, "tag", tag), params)
        return strategy

    p = Path(spec)
    if not p.exists():
        raise FileNotFoundError(f"Strategy not found: {spec}")

    mod = _load_module_from_path(p)
    if hasattr(mod, "build"):
        strategy = mod.build()
    elif hasattr(mod, "Strategy"):
        strategy = mod.Strategy()
    else:
        raise AttributeError(
            f"Strategy module {spec} must expose build() or Strategy class"
        )

    if not hasattr(strategy, "tag"):
        strategy.tag = p.stem
    return strategy


def load_strategies(specs: list[str]):
    return [load_strategy(spec) for spec in specs]

from __future__ import annotations

import importlib.util
from pathlib import Path

from strategies.builtin import build_strategy, built_in_strategy_factories


def _parse_value(raw: str):
    text = raw.strip()
    low = text.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _parse_builtin_spec(spec: str) -> tuple[str, dict]:
    # Format: tag|k=v|k=v
    parts = [p for p in spec.split("|") if p]
    tag = parts[0]
    overrides = {}
    for item in parts[1:]:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        overrides[k.strip()] = _parse_value(v)
    return tag, overrides


def _load_module_from_path(path: Path):
    module_name = f"soldem_strategy_{path.stem}_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load strategy module at {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_strategy(spec: str):
    factories = built_in_strategy_factories()
    base_tag, overrides = _parse_builtin_spec(spec)
    if base_tag in factories:
        return build_strategy(base_tag, overrides=overrides)

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

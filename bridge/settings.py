"""Environment-driven bridge configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BridgeSettings:
    sim_mode: str
    sim_hz: int
    isaac_sim_path: Path
    isaac_headless: bool
    isaac_auto_launch: bool

    @classmethod
    def from_env(cls) -> "BridgeSettings":
        sim_mode = os.environ.get("RAVEN_SIM_MODE", "isaac").strip().lower()
        if sim_mode not in {"isaac", "mock"}:
            raise ValueError("RAVEN_SIM_MODE must be either 'isaac' or 'mock'")

        sim_hz = int(os.environ.get("RAVEN_SIM_HZ", "20"))
        isaac_sim_path_raw = (
            os.environ.get("ISAAC_SIM_PATH")
            or os.environ.get("RAVEN_ISAAC_SIM_PATH")
            or str(Path.home() / "isaacsim")
        )
        isaac_sim_path = Path(isaac_sim_path_raw).expanduser()

        return cls(
            sim_mode=sim_mode,
            sim_hz=sim_hz,
            isaac_sim_path=isaac_sim_path,
            isaac_headless=_env_bool("RAVEN_ISAAC_HEADLESS", False),
            isaac_auto_launch=_env_bool("RAVEN_ISAAC_AUTO_LAUNCH", False),
        )

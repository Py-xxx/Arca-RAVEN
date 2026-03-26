"""Isaac Sim backend wrapper used by the bridge server."""

from __future__ import annotations

import importlib
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from simulation.core.catalog import DEFAULT_ROVER_TYPE, DEFAULT_TERRAIN, ROVER_WHEEL_COUNTS, TERRAINS
from simulation.core.simulation_interface import SimulationBackend


logger = logging.getLogger("raven.isaac")
BOOTSTRAP_RETRY_SECONDS = 5.0


class IsaacSimManager(SimulationBackend):
    mode = "isaac"

    def __init__(
        self,
        isaac_sim_path: str | Path | None = None,
        *,
        headless: bool = False,
        auto_launch: bool = False,
    ):
        self.isaac_sim_path = Path(isaac_sim_path).expanduser() if isaac_sim_path else Path.home() / "isaacsim"
        self.headless = headless
        self.auto_launch = auto_launch

        self.terrain = DEFAULT_TERRAIN
        self.rover_type = DEFAULT_ROVER_TYPE
        self.is_training = False
        self.episode = 0
        self.step = 0
        self.cumulative_reward = 0.0

        self._app: Any = None
        self._launch_process: subprocess.Popen[str] | None = None
        self._running = False
        self._state_provider: Callable[[], dict[str, Any] | None] | None = None
        self._status = "waiting_for_isaac"
        self._last_error: str | None = None
        self._next_bootstrap_attempt = 0.0
        self._embedded_runtime = False

    @property
    def ready(self) -> bool:
        return self._running and self._state_provider is not None

    def register_state_provider(self, provider: Callable[[], dict[str, Any] | None]) -> None:
        """Register the callback that returns live rover state from Isaac Sim."""
        self._state_provider = provider
        self._status = "streaming" if self._running else self._status

    def start(self) -> None:
        self._bootstrap(force=True)

    def stop(self) -> None:
        if self._app is not None:
            try:
                self._app.close()
            except Exception:
                logger.exception("Failed to close embedded Isaac Sim app cleanly")
            finally:
                self._app = None

        if self._launch_process is not None and self._launch_process.poll() is None:
            self._launch_process.terminate()
            self._launch_process = None

        self._running = False
        self._embedded_runtime = False
        if self._status == "streaming":
            self._status = "stopped"

    def tick(self) -> dict[str, Any] | None:
        self._bootstrap()

        if self._app is not None:
            try:
                self._app.update()
            except Exception as exc:
                self._last_error = f"Embedded Isaac Sim update failed: {exc}"
                self._status = "error"
                logger.exception("Embedded Isaac Sim update failed")
                self.stop()
                return None

        if self._state_provider is None:
            if self._running and self._status not in {"error", "streaming"}:
                self._status = "waiting_for_live_state"
            return None

        state = self._state_provider()
        if state is None:
            self._status = "waiting_for_live_state"
            return None

        self._status = "streaming"
        return state

    def get_config(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "ready": self.ready,
            "terrain": self.terrain,
            "rover_type": self.rover_type,
            "is_training": self.is_training,
            "available_terrains": list(TERRAINS.keys()),
            "available_rovers": list(ROVER_WHEEL_COUNTS.keys()),
        }

    def get_health(self) -> dict[str, Any]:
        return {
            "backend_status": self._status,
            "ready": self.ready,
            "isaac_sim_path": str(self.isaac_sim_path),
            "headless": self.headless,
            "auto_launch": self.auto_launch,
            "embedded_runtime": self._embedded_runtime,
            "last_error": self._last_error,
        }

    def set_terrain(self, terrain: str) -> None:
        if terrain in TERRAINS:
            self.terrain = terrain

    def set_rover(self, rover_type: str) -> None:
        if rover_type in ROVER_WHEEL_COUNTS:
            self.rover_type = rover_type

    def set_training(self, active: bool) -> None:
        self.is_training = active
        if active and self.step == 0:
            self.episode = 1

    def reset(self) -> None:
        self.step = 0
        self.episode = 0
        self.cumulative_reward = 0.0
        self.is_training = False

    def _bootstrap(self, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now < self._next_bootstrap_attempt:
            return
        self._next_bootstrap_attempt = now + BOOTSTRAP_RETRY_SECONDS

        if self._running:
            return

        if not self.isaac_sim_path.exists():
            self._status = "isaac_sim_not_found"
            self._last_error = f"Isaac Sim path does not exist: {self.isaac_sim_path}"
            return

        if self._try_start_embedded_app():
            self._running = True
            return

        if self.auto_launch:
            self._try_launch_process()

    def _try_start_embedded_app(self) -> bool:
        kit_extension = self.isaac_sim_path / "exts" / "omni.isaac.kit"
        if kit_extension.exists():
            path_str = str(kit_extension)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)

        try:
            simulation_app_module = importlib.import_module("omni.isaac.kit")
            simulation_app_cls = getattr(simulation_app_module, "SimulationApp")
        except Exception as exc:
            self._status = "waiting_for_isaac_runtime"
            self._last_error = f"Isaac Sim Python runtime is unavailable: {exc}"
            return False

        try:
            self._app = simulation_app_cls(
                {
                    "headless": self.headless,
                    "renderer": "RayTracedLighting",
                    "anti_aliasing": 3,
                }
            )
        except Exception as exc:
            self._status = "isaac_start_failed"
            self._last_error = f"Failed to start Isaac Sim: {exc}"
            logger.exception("Failed to start embedded Isaac Sim")
            self._app = None
            return False

        self._embedded_runtime = True
        self._status = "waiting_for_live_state"
        self._last_error = None
        logger.info("Isaac Sim embedded runtime started (headless=%s)", self.headless)
        return True

    def _try_launch_process(self) -> None:
        if self._launch_process is not None and self._launch_process.poll() is None:
            self._running = True
            self._status = "waiting_for_live_state"
            return

        executable = self._resolve_launcher()
        if executable is None:
            self._status = "isaac_launcher_not_found"
            self._last_error = f"No Isaac Sim launcher found under {self.isaac_sim_path}"
            return

        args = [str(executable)]
        if self.headless and executable.name.endswith(".sh"):
            args.append("--headless")

        try:
            self._launch_process = subprocess.Popen(args, cwd=self.isaac_sim_path)
        except Exception as exc:
            self._status = "isaac_launch_failed"
            self._last_error = f"Failed to launch Isaac Sim process: {exc}"
            logger.exception("Failed to launch Isaac Sim process")
            return

        self._running = True
        self._status = "waiting_for_live_state"
        self._last_error = None
        logger.info("Launched Isaac Sim process from %s", executable)

    def _resolve_launcher(self) -> Path | None:
        candidates = (
            self.isaac_sim_path / "isaac-sim.bat",
            self.isaac_sim_path / "isaac-sim.sh",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

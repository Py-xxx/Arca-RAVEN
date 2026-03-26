"""
Isaac Sim lifecycle manager.
Initialises the Omniverse Kit application, loads USD stages,
and provides a clean Python API to the rest of the simulation backend.

Isaac Sim 4.2+ must be installed at:
  ~/isaacsim   (default Omniverse path)
or the ISAAC_SIM_PATH environment variable must point to the install root.

Usage:
    manager = IsaacSimManager()
    manager.start()
    manager.load_scene("mars_crater_01")
    manager.step()
    manager.stop()
"""
import os
import sys
from pathlib import Path
from loguru import logger


ISAAC_SIM_PATH = Path(os.environ.get("ISAAC_SIM_PATH", Path.home() / "isaacsim"))


class IsaacSimManager:
    def __init__(self):
        self._app = None
        self._simulation_context = None
        self._running = False

    def start(self, headless: bool = False):
        """Boot the Isaac Sim Kit application."""
        kit_path = ISAAC_SIM_PATH / "kit" / "kit"
        if not kit_path.exists():
            raise FileNotFoundError(
                f"Isaac Sim not found at {ISAAC_SIM_PATH}. "
                "Install via NVIDIA Omniverse Launcher or set ISAAC_SIM_PATH."
            )
        sys.path.insert(0, str(ISAAC_SIM_PATH / "exts" / "omni.isaac.kit"))
        from omni.isaac.kit import SimulationApp  # type: ignore

        config = {
            "headless": headless,
            "renderer": "RayTracedLighting",
            "anti_aliasing": 3,
        }
        self._app = SimulationApp(config)
        logger.info(f"Isaac Sim started (headless={headless})")
        self._running = True

    def stop(self):
        if self._app:
            self._app.close()
            self._running = False
            logger.info("Isaac Sim stopped")

    @property
    def running(self) -> bool:
        return self._running

"""
Arca RAVEN — Bridge Server
FastAPI + WebSocket backend.
Defaults to Isaac Sim mode and stays idle until live telemetry is available.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

BRIDGE_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[1]
for path in (BRIDGE_DIR, ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from settings import BridgeSettings
from mock_sim import MockSimulation
from websocket_manager import ConnectionManager
from simulation.core.isaac_sim_manager import IsaacSimManager
from simulation.core.simulation_interface import SimulationBackend

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("raven.server")

SETTINGS = BridgeSettings.from_env()
SIM_HZ = SETTINGS.sim_hz  # ticks per second
SIM_INTERVAL = 1.0 / SIM_HZ

manager = ConnectionManager()


def create_simulation_backend() -> SimulationBackend:
    if SETTINGS.sim_mode == "mock":
        logger.warning("Bridge started in mock mode; set RAVEN_SIM_MODE=isaac for live data only.")
        return MockSimulation()

    return IsaacSimManager(
        isaac_sim_path=SETTINGS.isaac_sim_path,
        headless=SETTINGS.isaac_headless,
        auto_launch=SETTINGS.isaac_auto_launch,
    )


sim = create_simulation_backend()


@asynccontextmanager
async def lifespan(app: FastAPI):
    sim.start()
    task = asyncio.create_task(simulation_loop())
    logger.info("Arca RAVEN bridge server started (mode=%s)", sim.mode)
    yield
    task.cancel()
    sim.stop()
    logger.info("Bridge server stopped")


app = FastAPI(title="Arca RAVEN Bridge", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def simulation_loop():
    """Tick the simulation and broadcast state to all connected clients."""
    while True:
        if manager.count > 0:
            state = sim.tick()
            if state is not None:
                await manager.broadcast(state)
        await asyncio.sleep(SIM_INTERVAL)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": sim.mode,
        "clients": manager.count,
        "hz": SIM_HZ,
        **sim.get_health(),
    }


@app.get("/config")
async def get_config():
    return sim.get_config()


@app.post("/config/terrain/{terrain}")
async def set_terrain(terrain: str):
    sim.set_terrain(terrain)
    return {"terrain": sim.get_config()["terrain"]}


@app.post("/config/rover/{rover_type}")
async def set_rover(rover_type: str):
    sim.set_rover(rover_type)
    return {"rover_type": sim.get_config()["rover_type"]}


@app.post("/training/start")
async def start_training():
    sim.set_training(True)
    return {"is_training": True}


@app.post("/training/stop")
async def stop_training():
    sim.set_training(False)
    return {"is_training": False}


@app.post("/simulation/reset")
async def reset_simulation():
    sim.reset()
    return {"status": "reset"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Listen for control messages from the frontend
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "set_terrain":
                    sim.set_terrain(msg["terrain"])
                elif msg.get("type") == "set_rover":
                    sim.set_rover(msg["rover_type"])
                elif msg.get("type") == "set_training":
                    sim.set_training(msg["active"])
                elif msg.get("type") == "reset":
                    sim.reset()
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8765, reload=True)

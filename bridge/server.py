"""
Arca RAVEN — Bridge Server
FastAPI + WebSocket backend. Runs in mock mode by default.
Isaac Sim integration added in Phase 2.
"""

import asyncio
import logging
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from mock_sim import MockSimulation
from websocket_manager import ConnectionManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("raven.server")

SIM_HZ = 20  # ticks per second
SIM_INTERVAL = 1.0 / SIM_HZ

sim = MockSimulation()
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulation_loop())
    logger.info("Arca RAVEN bridge server started (mock mode)")
    yield
    task.cancel()
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
            await manager.broadcast(state)
        await asyncio.sleep(SIM_INTERVAL)


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "mock", "clients": manager.count, "hz": SIM_HZ}


@app.get("/config")
async def get_config():
    return {
        "terrain": sim.terrain,
        "rover_type": sim.rover_type,
        "is_training": sim.is_training,
        "available_terrains": list(MockSimulation.TERRAINS.keys()),
        "available_rovers": list(MockSimulation.ROVER_WHEEL_COUNTS.keys()),
    }


@app.post("/config/terrain/{terrain}")
async def set_terrain(terrain: str):
    sim.set_terrain(terrain)
    return {"terrain": sim.terrain}


@app.post("/config/rover/{rover_type}")
async def set_rover(rover_type: str):
    sim.set_rover(rover_type)
    return {"rover_type": sim.rover_type}


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
    sim.t = 0.0
    sim.step = 0
    sim.episode = 0
    sim.cumulative_reward = 0.0
    sim.is_training = False
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
                    sim.t = 0.0
                    sim.step = 0
                    sim.episode = 0
                    sim.cumulative_reward = 0.0
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8765, reload=True)

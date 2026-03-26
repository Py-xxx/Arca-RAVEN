"""
FastAPI server — bridge between Tauri frontend and Isaac Sim backend.
Handles WebSocket streaming for real-time simulation state and REST
endpoints for configuration, training control, and model management.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RL Rover Simulation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "isaac_sim_connected": False}

# Routers registered in Phase 1 development:
# from simulation.api.routes import simulation, training, rovers, terrain
# app.include_router(simulation.router, prefix="/simulation")
# app.include_router(training.router,   prefix="/training")
# app.include_router(rovers.router,     prefix="/rovers")
# app.include_router(terrain.router,    prefix="/terrain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simulation.api.server:app", host="127.0.0.1", port=8765, reload=False)

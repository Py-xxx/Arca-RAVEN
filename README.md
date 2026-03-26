# Arca RAVEN

**Autonomous Planetary Rover Training Platform**

RAVEN is a high-fidelity simulation and reinforcement learning platform for training autonomous rovers to navigate extraterrestrial and off-road terrain. Built by Arca.

## Status

The backend is now wired to default to `isaac` mode. No machine-specific Isaac Sim path is hardcoded in the repo. Set `ISAAC_SIM_PATH` at runtime on the machine that is running Isaac Sim.

The current Isaac integration is startup and health-check wiring, not full live telemetry. Until a real Isaac state provider is registered, the app should remain idle instead of showing fake rover data.

## Quick Start

### Backend
```bash
cd bridge
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

Important:

- The bridge defaults to `isaac` mode.
- Set `ISAAC_SIM_PATH` on the Windows machine before starting the backend if Isaac Sim is not installed in the default location.
- Use `RAVEN_SIM_MODE=mock` only if you explicitly want the legacy mock backend.

### Frontend
```bash
cd app
npm install
npm run tauri dev
```

## Windows Validation

For the Windows machine test flow, see [docs/windows-test-flow.md](docs/windows-test-flow.md).

## Reference

See `instructions.md` for the full project specification and development roadmap.

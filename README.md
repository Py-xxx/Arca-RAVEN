# Arca RAVEN

**Autonomous Planetary Rover Training Platform**

RAVEN is a high-fidelity simulation and reinforcement learning platform for training autonomous rovers to navigate extraterrestrial and off-road terrain. Built by Arca.

## Quick Start

### Backend (Mock Mode — no Isaac Sim required)
```bash
cd bridge
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### Frontend
```bash
cd app
npm install
npm run tauri dev
```

See `instructions.md` for the full project specification and development roadmap.
# Arca-RAVEN

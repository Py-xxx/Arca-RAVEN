#!/usr/bin/env bash
# RL Rover Control — full environment setup
# Run this once after cloning the repo.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== RL Rover Control Setup ==="

# ── Python virtual environment ──────────────────────────────────────────────
echo "[1/4] Creating Python virtual environment..."
python3 -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip wheel
pip install -r "$ROOT/simulation/requirements.txt"
echo "      Python venv ready at .venv/"

# ── Node / Tauri ─────────────────────────────────────────────────────────────
echo "[2/4] Installing Node dependencies..."
cd "$ROOT/app"
npm install
echo "      Node deps ready."

# ── Rust (Tauri backend) ─────────────────────────────────────────────────────
echo "[3/4] Checking Rust toolchain..."
if ! command -v cargo &>/dev/null; then
  echo "      Rust not found. Install from https://rustup.rs then re-run."
  exit 1
fi
echo "      Rust $(rustc --version) found."

# ── Isaac Sim check ──────────────────────────────────────────────────────────
echo "[4/4] Checking Isaac Sim installation..."
ISAAC_PATH="${ISAAC_SIM_PATH:-$HOME/isaacsim}"
if [ -d "$ISAAC_PATH" ]; then
  echo "      Isaac Sim found at $ISAAC_PATH"
else
  echo ""
  echo "  !! Isaac Sim NOT found at $ISAAC_PATH"
  echo "     Install via NVIDIA Omniverse Launcher (Isaac Sim 4.2+)"
  echo "     Then set: export ISAAC_SIM_PATH=/path/to/isaacsim"
  echo ""
fi

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Install Isaac Sim 4.2+ if not done"
echo "  2. Clone Isaac Lab: https://github.com/isaac-sim/IsaacLab"
echo "  3. Download terrain heightmaps (see instructions.md § Assets)"
echo "  4. Download rover USD models (see instructions.md § Assets)"
echo "  5. Run backend: source .venv/bin/activate && python -m simulation.api.server"
echo "  6. Run frontend: cd app && npm run tauri dev"

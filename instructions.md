# Arca RAVEN — Project Specification

**RAVEN** (Reinforcement-learning Autonomous Vehicle for Extraterrestrial Navigation)  
**Brand:** Arca | **Unit:** RAVEN | **Version:** 0.1.0

---

## 1. Vision

Arca RAVEN is a high-fidelity simulation and reinforcement learning platform for training autonomous rovers to navigate extraterrestrial and off-road terrain. The platform simulates real-world physics, sensors, and environments to produce trained RL policies that transfer directly to physical hardware with minimal sim-to-real gap.

The goal is a complete pipeline: design scenario → train policy → deploy to real rover.

RAVEN is not a game or a toy simulation. Every physics value, sensor noise model, terrain parameter, and reward signal is grounded in real planetary science and robotics engineering practice. The target real-world hardware is the NVIDIA Jetson AGX Orin, the same platform used in serious autonomous robot deployments.

---

## 2. Core Requirements

- High-fidelity physics — no simplified approximations. Terramechanics, wheel-soil interaction, realistic gravity per environment.
- Real-time 3D visualization of the rover navigating terrain.
- Full sensor simulation: LiDAR, stereo cameras, IMU, GPS, wheel encoders — all with hardware-accurate noise models.
- RL training pipeline: train a policy in simulation, watch performance improve in real time.
- Multi-terrain support: Mars, Moon, Asteroid, Earth off-road, and custom user-defined terrain.
- Multi-rover support: start with wheeled (rocker-bogie, skid-steer), expandable to tracked.
- Sim-to-real deployment: export trained policy as ONNX → TensorRT → run on Jetson AGX Orin via ROS2.
- Mac-compatible development: full frontend and backend structure can be developed on macOS. Isaac Sim runs only on Windows/Linux with NVIDIA GPU.
- Single-installer distribution: the Python bridge server is bundled into the Tauri app as a sidecar process via PyInstaller. The end user installs one executable and the entire app starts automatically. Isaac Sim is installed separately by the user.
- No data until connected: when Isaac Sim is not running or not connected, the app shows an idle/waiting state. No mock data is shown in production. Mock mode exists only during development and will be removed before final distribution.

---

## 3. Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Physics / Simulation | NVIDIA Isaac Sim | 4.2+ | PhysX 5, RTX sensor sim, USD scenes |
| RL Training | Isaac Lab | Latest | GPU-parallel environments on RTX 3060 |
| RL Algorithms | Stable Baselines3 / RSL_RL | SB3 2.3+ | SAC primary, PPO curriculum bootstrap |
| Deep Learning | PyTorch | 2.x | Policy networks, ONNX export |
| Backend Bridge | FastAPI + Uvicorn | 0.115 / 0.30 | WebSocket at 20 Hz, REST config API |
| Sidecar Bundler | PyInstaller | 6.x | Packages Python bridge into a single binary bundled inside Tauri |
| Frontend Shell | Tauri | 2.x | Native desktop wrapper — spawns Python sidecar on launch |
| Frontend UI | React + TypeScript | 18 / 5.x | Component-based mission control |
| 3D Viewport | Three.js | 0.170+ | Viewport placeholder; full scene in Isaac Sim |
| State Management | Zustand | 5.x | Reactive rover state store |
| Charts | Recharts | 2.x | Training reward curves, episode stats |
| Real-world Middleware | ROS2 Humble | LTS | Sensor topics, motor commands |
| Policy Export | ONNX + TensorRT | — | Jetson inference |
| Real Hardware | NVIDIA Jetson AGX Orin | — | Same CUDA ecosystem as training |

---

## 4. Architecture

### 4.1 Overview

```
User launches Arca RAVEN installer
  └── Tauri App starts
        └── Tauri spawns Python bridge server (sidecar — bundled via PyInstaller)

Tauri App (Mission Control UI)
  ├── 3D Viewport (Three.js placeholder → Isaac Sim viewport)
  ├── Telemetry Panel (position, orientation, velocity)
  ├── Sensor Panel (LiDAR viz, IMU, GPS)
  ├── Training Dashboard (reward curves, episode stats)
  └── Mission Panel (rover / terrain selection, controls)
         │
         │ WebSocket (ws://localhost:8765/ws) — 20 Hz
         │ REST    (http://localhost:8765)    — config & commands
         ▼
Python Bridge Server (FastAPI) ← sidecar, auto-started by Tauri
  ├── Dev Mode: mock_sim.py (development only — removed before distribution)
  └── Production Mode: waits for Isaac Sim connection, streams nothing until connected
         │
         ▼ (only when Isaac Sim is running)
Isaac Sim / Isaac Lab  ← installed separately by the user (NVIDIA Omniverse Launcher)
  ├── Physics: PhysX 5 (rigid body, articulation, deformable terrain)
  ├── Sensors: Ouster OS1-64 LiDAR, RealSense D435, VectorNav VN-200 IMU
  ├── RL Env: Isaac Lab Gym (parallel envs, reward, curriculum)
  └── Policy: SAC/PPO → ONNX → TensorRT → Jetson AGX Orin

Disconnected state (Isaac Sim not running):
  └── All panels show idle/waiting UI — no data, no placeholders, no mock values
```

### 4.2 WebSocket Message Schema

All state messages from the bridge follow this JSON schema at 20 Hz:

```json
{
  "type": "rover_state",
  "timestamp": 1234567890.123,
  "rover": {
    "id": "raven-001",
    "type": "rocker_bogie",
    "position": { "x": 0.0, "y": 0.0, "z": 0.15 },
    "orientation": { "roll": 0.0, "pitch": 0.0, "yaw": 0.0 },
    "velocity": { "linear": 0.08, "angular": 0.001 },
    "wheel_speeds": [0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
  },
  "sensors": {
    "imu": {
      "accelerometer": { "x": 0.0, "y": 0.0, "z": -3.72 },
      "gyroscope": { "x": 0.0, "y": 0.0, "z": 0.0 }
    },
    "lidar": { "ranges": [10.0, ...], "min_range": 0.3, "max_range": 50.0, "num_rays": 360 },
    "gps": { "latitude": -4.5895, "longitude": 137.4417, "altitude": -4500.0 }
  },
  "training": {
    "episode": 0, "step": 0, "reward": 0.0, "cumulative_reward": 0.0, "is_training": false
  },
  "environment": {
    "terrain": "mars", "gravity": -3.72, "description": "Gale Crater, Mars", "simulation_time": 0.0
  }
}
```

### 4.3 Control Messages (Frontend → Bridge)

```json
{ "type": "set_terrain",  "terrain": "mars" }
{ "type": "set_rover",    "rover_type": "rocker_bogie" }
{ "type": "set_training", "active": true }
{ "type": "reset" }
```

---

## 5. Project Structure

```
arca-raven/
├── instructions.md          ← This file
├── .gitignore
├── README.md
├── bridge/                  ← FastAPI bridge server
│   ├── server.py            ← Entry point (uvicorn)
│   ├── mock_sim.py          ← Mock physics for Mac development
│   ├── websocket_manager.py ← WebSocket connection pool
│   └── requirements.txt
├── simulation/              ← Isaac Sim integration (Phase 2+)
│   └── environments/
├── training/                ← Isaac Lab RL (Phase 4+)
│   ├── environments/        ← Gym env definitions
│   ├── rewards/             ← Composite reward functions
│   ├── curriculum/          ← Stage scheduler
│   └── configs/
│       └── default.yaml     ← Training hyperparameters
├── rovers/                  ← USD articulation models (Phase 2+)
├── terrain/                 ← USD terrain scenes (Phase 2+)
├── models/                  ← Saved policies & ONNX exports
├── deployment/              ← Jetson deployment scripts (Phase 7)
├── docs/
│   └── architecture.md
└── app/                     ← Tauri + React frontend
    ├── src/
    │   ├── components/
    │   │   ├── layout/      ← Header
    │   │   ├── viewport/    ← Three.js 3D scene
    │   │   ├── telemetry/   ← Position / orientation / velocity
    │   │   ├── sensors/     ← LiDAR viz, IMU, GPS
    │   │   ├── training/    ← Reward chart, episode stats
    │   │   └── mission/     ← Rover & terrain selection
    │   ├── store/           ← Zustand state
    │   ├── hooks/           ← WebSocket auto-connect
    │   └── types/           ← TypeScript interfaces
    └── src-tauri/           ← Rust/Tauri shell
```

---

## 6. Terrains

Each terrain is a complete simulation environment with specific physics parameters, soil model, and sensor behavior.

| ID | Name | Gravity | Based On | Soil Model | Notes |
|---|---|---|---|---|---|
| `mars` | Gale Crater, Mars | −3.72 m/s² | NASA Curiosity landing site | SCM basalt regolith | Primary development terrain |
| `moon` | Mare Tranquillitatis | −1.62 m/s² | Apollo 11 landing site | SCM fine-grain dust | Very different slip behavior vs Mars |
| `asteroid` | 433 Eros | −0.003 m/s² | Near-Earth asteroid | Granular mechanics | Micro-gravity — requires anchor/thruster dynamics |
| `earth` | Mojave Desert, CA | −9.81 m/s² | JPL test range analog | Mixed soil, gravel | Used as analog terrain by NASA |
| `custom` | User-defined | Configurable | GeoTIFF heightmap import | Configurable | Phase 6+ |

### Terrain Scene Format
- **USD** (Universal Scene Description) — Isaac Sim native format
- **SCM** (Soil Contact Model) — deformable terrain that reacts to wheel load
- Heightmap resolution: 1cm/pixel for close terrain, 1m/pixel for background
- Rock/obstacle placement: procedural + manual placement tools (Phase 6)

---

## 7. Rovers

| ID | Name | Wheels | Based On | Wheel Diameter | Max Speed |
|---|---|---|---|---|---|
| `rocker_bogie` | 6-Wheel Rocker-Bogie | 6 | NASA Curiosity / Perseverance | 0.5m | 0.14 m/s |
| `skid_steer` | 4-Wheel Skid-Steer | 4 | Generic utility rover | 0.3m | 0.5 m/s |
| `tracked` | Tracked Rover | — | Future phase | — | — |

### Rover Model Format
- USD articulation with joint definitions for each wheel/rocker arm
- URDF export for ROS2 compatibility
- Sensor mount offsets defined per rover type in config

---

## 8. Sensors

All sensors are simulated using Isaac Sim's RTX-based sensor pipeline, matching the behavior of real hardware components used in field robotics.

### 8.1 LiDAR — Ouster OS1-64
- 64 vertical channels, 360° horizontal sweep
- Range: 0.3m – 120m
- Angular resolution: 0.35° horizontal
- Update rate: 20 Hz
- Noise model: Gaussian + dropout based on surface reflectivity
- Output: full point cloud (XYZ + intensity) + 2D range image

### 8.2 Stereo Camera — Intel RealSense D435
- RGB: 1920×1080 @ 30 fps
- Depth: 848×480 @ 90 fps
- Baseline: 50mm
- FOV: 86°×57° (RGB), 87°×58° (depth)
- Noise: Gaussian + structured light artifacts

### 8.3 IMU — VectorNav VN-200
- Accelerometer: ±16g, 0.14 mg/√Hz noise density
- Gyroscope: ±2000°/s, 0.0035°/s/√Hz noise density
- Update rate: 400 Hz (decimated to 100 Hz for RL)
- Gravity compensation per terrain environment

### 8.4 GPS — u-blox F9P
- Position accuracy: 0.01m (RTK), 1.5m (standalone)
- Update rate: 20 Hz
- On-Earth only — replaced with relative positioning for Moon/Asteroid
- Noise model: HDOP-scaled Gaussian

### 8.5 Wheel Encoders
- 1024 CPR (counts per revolution)
- Used for odometry and wheel slip detection
- Slip ratio computed per wheel: (wheel_speed - rover_speed) / max(wheel_speed, 0.001)

---

## 9. Reinforcement Learning

### 9.1 Observation Space

At each timestep, the policy receives:

| Component | Shape | Description |
|---|---|---|
| LiDAR ranges | (360,) | Normalized range values [0, 1] |
| IMU accelerometer | (3,) | m/s² values |
| IMU gyroscope | (3,) | rad/s values |
| Rover orientation | (3,) | roll, pitch, yaw in radians |
| Rover velocity | (2,) | linear and angular |
| Goal direction | (2,) | bearing and distance to goal |
| History stack | ×4 | Last 4 observation frames stacked |

Total observation dimension: ~1500 (with LiDAR history)

### 9.2 Action Space

Continuous action space:
- Left side wheel speed: [−1, 1] normalized → scaled to [−0.14, 0.14] m/s
- Right side wheel speed: [−1, 1] normalized → scaled to [−0.14, 0.14] m/s

Differential drive control. The rocker-bogie passive suspension handles individual wheel adaptation.

### 9.3 Reward Function

```python
reward = (
    w_progress   * progress_toward_goal       # +  forward movement
  + w_tilt       * tilt_penalty               # -  tip-over risk (roll/pitch)
  + w_slip       * wheel_slip_penalty         # -  terrain damage + energy waste
  + w_hazard     * proximity_to_hazard        # -  safety margin violations
  + w_power      * motor_power_penalty        # -  battery efficiency
  + w_smooth     * path_smoothness_bonus      # +  mechanical wear reduction
  + w_success    * goal_reached_bonus         # +  episode success
  + w_death      * tip_over_penalty           # -  episode termination penalty
)
```

Default weights (from `training/configs/default.yaml`):
- progress: 1.0, tilt: −2.0, slip: −0.5, hazard: −1.5, power: −0.3, smooth: 0.2

### 9.4 Curriculum

Training progresses through stages automatically when mean reward exceeds the stage threshold:

1. **Flat** — no obstacles, 2° max slope. Learn basic locomotion.
2. **Gentle Slopes** — 10° max slope, sparse rocks. Learn slope handling.
3. **Rocky** — 20° max slope, 20% rock density. Learn obstacle avoidance.
4. **Full Hazard** — 30° max slope, 40% rock density, loose soil. Full deployment conditions.

### 9.5 Algorithms

| Algorithm | Use Case | Notes |
|---|---|---|
| **SAC** (Soft Actor-Critic) | Primary training | Best for continuous control, sample efficient |
| **PPO** (Proximal Policy Optimization) | Curriculum bootstrap | Stable for early curriculum stages |
| **TD3** | Comparison baseline | Deterministic policy, good for evaluation |

### 9.6 Training Infrastructure

- **Isaac Lab** runs parallel GPU environments on the RTX 3060 12GB
- Recommended: 64–128 parallel environments (within 12GB VRAM)
- Use headless rendering during training; switch to full quality for eval runs
- Policy network: MLP with [512, 256, 128] hidden layers + LayerNorm
- Expected training time on RTX 3060: ~4–8 hours per curriculum stage

---

## 10. Sim-to-Real Pipeline

```
Trained PyTorch Policy
       │
       ▼ torch.onnx.export()
  ONNX Model (.onnx)
       │
       ▼ trtexec (on Jetson AGX Orin)
TensorRT Engine (.engine)
       │
       ▼ ROS2 Inference Node
Real Sensor Drivers → [LiDAR, Camera, IMU, GPS] → Observation Builder → Policy Inference → Motor Commands → Rover
```

### Domain Randomization (Sim-to-Real Gap Reduction)

During training, randomize:
- Terrain friction coefficient: ±30%
- Sensor noise magnitude: ±50%
- Rover mass: ±10%
- Gravity: ±1% (sensor calibration error)
- Actuator delay: 0–50ms

---

## 11. Development Phases

### Phase 1 — Foundation (Mac-compatible)
**Goal:** Running Tauri app with live mock telemetry and full navigation UI.
- [x] Project directory structure
- [x] FastAPI bridge server with mock simulation (20 Hz) — development only
- [x] WebSocket streaming rover state
- [x] Tauri + React frontend shell
- [x] 3D viewport (Three.js — rover moves based on mock data)
- [x] Telemetry panel (position, orientation, velocity, GPS)
- [x] Sensor panel (LiDAR polar viz, IMU)
- [x] Training dashboard (reward chart, episode counter)
- [x] Mission panel (rover and terrain selection)
- [ ] Full sidebar navigation with dedicated pages (Mission Control, Training, Sensor Lab, Fleet, Terrain, Models, Settings)
- [ ] Idle/waiting state for all panels when Isaac Sim is disconnected
- **Note:** Mock mode (`mock_sim.py`) is used during Phase 1 development only. It will be removed before Phase 2 distribution. In production, the app shows a waiting state when Isaac Sim is not connected.
- **Acceptance:** App runs, all pages navigate correctly, idle states display cleanly, mock data drives panels during development.

### Phase 2 — Isaac Sim Integration (Windows + RTX GPU required)
**Goal:** Real physics replacing mock simulation.
- [ ] Install Isaac Sim 4.2 via NVIDIA Omniverse Launcher
- [ ] Create rocker-bogie rover USD model
- [ ] Create Mars terrain USD scene
- [ ] Isaac Sim Python API bridge replacing mock_sim.py
- [ ] Real PhysX physics driving rover state
- [ ] RTX sensor simulation (LiDAR, IMU)
- **Acceptance:** Rover drives across Mars terrain in Isaac Sim; all panels in Tauri update from real physics data.

### Phase 3 — Full Sensor Suite
**Goal:** All sensors simulated and streaming.
- [ ] Ouster OS1-64 LiDAR (full point cloud)
- [ ] RealSense D435 stereo camera (RGB + depth frames to Tauri)
- [ ] VectorNav VN-200 IMU with noise model
- [ ] u-blox F9P GPS with HDOP noise model
- [ ] Wheel encoder simulation + slip detection
- **Acceptance:** All sensor panels in Tauri show real Isaac Sim data. LiDAR point cloud renders correctly.

### Phase 4 — RL Training Pipeline
**Goal:** Train a policy that navigates to a goal.
- [ ] Isaac Lab Gym environment wrapping the Isaac Sim scene
- [ ] Composite reward function implementation
- [ ] Curriculum stage 1 (flat terrain) training
- [ ] Training dashboard shows live reward curves from actual training
- [ ] Policy evaluation: run trained policy in simulation and watch in Tauri
- **Acceptance:** Policy learns to navigate flat terrain to goal. Reward curve shows improvement over training.

### Phase 5 — Curriculum and Multi-Terrain
**Goal:** Policy that handles all terrain types.
- [ ] All 4 terrain presets in Isaac Sim
- [ ] Curriculum scheduler (auto-advance stages)
- [ ] Domain randomization pipeline
- [ ] Policy comparison: before/after training runs side-by-side
- **Acceptance:** Policy trained to full_hazard stage. Performance measurably better than untrained on all terrains.

### Phase 6 — Multi-Rover and Custom Terrain
**Goal:** Full rover and terrain selection system.
- [ ] 4-wheel skid-steer USD model
- [ ] Per-rover reward weight tuning
- [ ] Custom terrain: GeoTIFF heightmap import
- [ ] Procedural rock/obstacle placement tool
- **Acceptance:** Both rover types train successfully. User can import a heightmap and train on it.

### Phase 7 — Sim-to-Real Deployment
**Goal:** Trained policy runs on real Jetson hardware.
- [ ] ONNX export from trained PyTorch policy
- [ ] TensorRT conversion on Jetson AGX Orin
- [ ] ROS2 Humble inference node
- [ ] Real sensor driver integration (ROS2 topics)
- [ ] Hardware-in-the-loop test
- **Acceptance:** Policy exported from simulation controls a real rover via ROS2 without modification.

### Phase 8 — Distribution Build
**Goal:** Single-installer app for end users. No terminal required.
- [ ] PyInstaller packages `bridge/server.py` and all Python deps into `raven-bridge` binary
- [ ] Binary placed in `app/src-tauri/binaries/` as a Tauri sidecar
- [ ] `tauri.conf.json` updated with sidecar permissions
- [ ] Rust `lib.rs` updated to spawn and kill sidecar on app open/close
- [ ] Remove `mock_sim.py` and all mock mode references from production bridge
- [ ] Bridge server production mode: shows idle state, polls for Isaac Sim connection, streams data only when connected
- [ ] App shows full-screen "Waiting for Isaac Sim" screen when bridge has no simulation connected
- [ ] `npm run tauri build` produces platform installer (`.exe` on Windows, `.dmg` on macOS)
- **Acceptance:** User installs one file, opens the app, sees idle state, launches Isaac Sim, app automatically connects and all panels populate.

---

## 12. Setup Instructions

### Backend (Bridge Server)
```bash
cd bridge
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py               # starts on ws://localhost:8765
```

### Frontend (Tauri App)
```bash
# Prerequisites: Node.js 20+, Rust (rustup), Tauri CLI
cd app
npm install
npm run tauri dev
```

### Isaac Sim (Windows / Linux + NVIDIA GPU only — installed separately)
1. Install NVIDIA Omniverse Launcher from https://www.nvidia.com/en-us/omniverse/
2. Install Isaac Sim 4.2+ from the Omniverse Launcher
3. Install Isaac Lab following official docs at https://isaac-sim.github.io/IsaacLab/
4. Run `simulation/setup.py` (Phase 2+)

### Production Build (Phase 8)
```bash
# 1. Package Python bridge as sidecar binary
cd bridge
pip install pyinstaller
pyinstaller --onefile --name raven-bridge server.py
# Copy dist/raven-bridge to app/src-tauri/binaries/

# 2. Build Tauri installer
cd app
npm run tauri build
# Output: app/src-tauri/target/release/bundle/
```

---

## 13. Key Design Decisions

- **Isaac Sim over Chrono:** Isaac Sim has the best RTX sensor simulation and the tightest Isaac Lab integration for RL. RTX 3060 12GB is sufficient.
- **Tauri as UI shell:** Isaac Sim owns the physics and 3D rendering. Tauri owns mission control, training monitoring, and config — this is the clean split.
- **Mock mode first, removed later:** All UI development happens on Mac with fake data. Isaac Sim is plugged in on Windows in Phase 2. Mock mode (`mock_sim.py`) is deleted before Phase 8 distribution — it is a development tool only, never shipped to users.
- **Idle state over fake data:** When Isaac Sim is not connected in production, every panel shows a clean waiting state. No dummy values, no placeholder numbers. This prevents users from confusing simulated data with real data.
- **Sidecar for single-installer distribution:** PyInstaller bundles the Python bridge into a self-contained binary. Tauri spawns it on launch and kills it on close. The user installs one file and needs no Python, no terminal, no manual server start. Isaac Sim itself is the one external dependency — it is too large (~50GB) to bundle and must be installed separately via NVIDIA Omniverse Launcher.
- **SAC primary algorithm:** SAC is the current state-of-the-art for continuous control in robotics. More sample-efficient than PPO for this action space.
- **ROS2 for real-world:** All output formats are ROS2-compatible from Phase 3 onward. This means the sim and real hardware share the same message types.
- **Jetson AGX Orin target:** Same CUDA ecosystem as training hardware. TensorRT inference runs the identical policy without retraining.
- **USD scene format:** Isaac Sim native, supports parametric scenes, photorealistic materials, and sensor placement. All terrain and rover assets in USD.

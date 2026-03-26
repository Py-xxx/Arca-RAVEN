# Arca RAVEN Windows Test Flow

This document describes the current Windows testing flow for validating the repo against a local Isaac Sim installation.

The repo does not hardcode an Isaac Sim path. The install location is provided at runtime through environment variables, so the same codebase can be used on different machines.

## Current Scope

This flow verifies:

- the repo can be cloned and started on Windows
- the bridge can run in `isaac` mode
- the bridge can resolve your local Isaac Sim install path
- the frontend can connect to the bridge
- the app remains idle instead of showing mock telemetry when live Isaac data is not available

This flow does not yet provide live rover telemetry from Isaac Sim. The current backend is wired for Isaac-first startup and health reporting, but the real scene/state provider still needs to be implemented.

## Prerequisites

Before starting, make sure the Windows PC already has:

- Git
- Python 3 and `venv`
- Node.js and npm
- Rust/Tauri Windows prerequisites
- Isaac Sim installed locally

ROS 2 in WSL2 is optional for this test flow. It is not required to boot the bridge or frontend.

## 1. Clone the Repository

Open PowerShell and clone the repo:

```powershell
git clone <your-repo-url>
cd "<repo-folder>"
```

## 2. Set Isaac Sim Runtime Variables

Set the environment variables in the same PowerShell session you will use for the backend:

```powershell
$env:RAVEN_SIM_MODE = "isaac"
$env:ISAAC_SIM_PATH = "G:\Isaac Sim"
$env:RAVEN_ISAAC_AUTO_LAUNCH = "false"
$env:RAVEN_ISAAC_HEADLESS = "false"
$env:RAVEN_SIM_HZ = "20"
```

Notes:

- Replace `G:\Isaac Sim` with the local install path on that machine.
- Paths with spaces are fine as long as they stay quoted.
- Do not commit machine-specific paths into the repo.

## 3. Start the Bridge

From the repo root:

```powershell
cd bridge
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

The bridge defaults to `isaac` mode unless you override `RAVEN_SIM_MODE`.

## 4. Verify Bridge Health

With the bridge running, open a browser or use PowerShell:

```powershell
Invoke-WebRequest http://localhost:8765/health | Select-Object -Expand Content
Invoke-WebRequest http://localhost:8765/config | Select-Object -Expand Content
```

Expected results today:

- `mode` should be `isaac`
- `isaac_sim_path` should match the path you set
- `backend_status` should reflect the current startup state

Common `backend_status` values:

- `isaac_sim_not_found`: the path is wrong
- `waiting_for_isaac_runtime`: the Isaac Python runtime is not available to the bridge yet
- `waiting_for_live_state`: Isaac startup is acceptable, but no live rover state provider is connected yet
- `isaac_launcher_not_found`: auto-launch was requested, but no launcher script was found
- `isaac_launch_failed`: the bridge tried to launch Isaac Sim and failed

At this stage, `ready` may still be `false`. That is expected until live Isaac rover state is wired in.

## 5. Launch Isaac Sim

If you are launching Isaac Sim manually:

```powershell
& "G:\Isaac Sim\isaac-sim.bat"
```

If you want the bridge to try launching it for you, set:

```powershell
$env:RAVEN_ISAAC_AUTO_LAUNCH = "true"
```

and restart the bridge.

Manual launch is the safer option while the integration is still early.

## 6. Start the Frontend

Open a second PowerShell window from the repo root:

```powershell
cd app
npm install
npm run tauri dev
```

## 7. Expected App Behavior Today

With the current codebase, the expected behavior is:

- the frontend connects to the bridge
- the bridge reports Isaac-mode health correctly
- the app does not show fake rover telemetry
- the panels remain idle until real Isaac state starts streaming

This idle behavior is correct and intentional. No mock data should appear in the normal Windows Isaac test path.

## 8. Troubleshooting

If the bridge reports `isaac_sim_not_found`:

- re-check `ISAAC_SIM_PATH`
- make sure the path exists on the Windows machine

If the bridge imports fail:

- activate `bridge/.venv`
- reinstall bridge dependencies with `pip install -r requirements.txt`

If your Isaac path contains spaces:

- keep it quoted in PowerShell and when launching manually

If the frontend starts but shows no telemetry:

- that is the expected current behavior
- the live Isaac scene/state provider is the next implementation milestone

## 9. Next Step After This Test Flow

Once this flow is stable on Windows, the next backend task is:

- create a real Isaac Sim state provider
- register it with the bridge
- stream real rover pose, sensors, and simulation time using the existing frontend message schema

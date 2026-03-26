# Arca RAVEN — Architecture

See `instructions.md` in the root for the full specification.

This document covers runtime data flow.

## WebSocket Message Format

All messages from the bridge server follow this schema:

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
    "lidar": {
      "ranges": [10.0, 10.1, ...],
      "min_range": 0.3,
      "max_range": 50.0,
      "num_rays": 360
    },
    "gps": {
      "latitude": -4.5895,
      "longitude": 137.4417,
      "altitude": -4500.0
    }
  },
  "training": {
    "episode": 0,
    "step": 0,
    "reward": 0.0,
    "cumulative_reward": 0.0,
    "is_training": false
  },
  "environment": {
    "terrain": "mars",
    "gravity": -3.72,
    "description": "Gale Crater, Mars",
    "simulation_time": 0.0
  }
}
```

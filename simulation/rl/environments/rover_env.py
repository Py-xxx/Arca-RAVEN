"""
Gymnasium environment wrapping the Isaac Sim simulation.
Observation and action spaces defined here map 1:1 to real hardware I/O.

Observation space (concatenated flat vector + structured dict):
  - lidar_ranges:    (N_BEAMS,)        float32  — normalised [0,1]
  - camera_depth:    (H, W, 1)         float32  — normalised depth image
  - imu_accel:       (3,)              float32  — m/s²  (x, y, z)
  - imu_gyro:        (3,)              float32  — rad/s (roll, pitch, yaw rate)
  - pose_local:      (6,)              float32  — (x,y,z, roll,pitch,yaw)
  - goal_vector:     (3,)              float32  — direction + distance to goal
  - wheel_speeds:    (N_WHEELS,)       float32  — current wheel velocities

Action space (continuous):
  - wheel_torques:   (N_WHEELS,)       float32  — normalised [-1, 1]
  OR
  - velocity_cmd:    (2,)              float32  — (linear_vel, angular_vel)

Both action modes supported; default is velocity_cmd (higher-level, safer).
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces


N_LIDAR_BEAMS = 360       # Horizontal scan points per sweep
LIDAR_MAX_RANGE = 20.0    # metres
CAMERA_H, CAMERA_W = 128, 128
N_WHEELS_DEFAULT = 6      # Rocker-bogie


class RoverEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, config: dict | None = None):
        super().__init__()
        self.config = config or {}
        n_wheels = self.config.get("n_wheels", N_WHEELS_DEFAULT)

        self.observation_space = spaces.Dict({
            "lidar_ranges":  spaces.Box(0.0, 1.0, (N_LIDAR_BEAMS,), np.float32),
            "camera_depth":  spaces.Box(0.0, 1.0, (CAMERA_H, CAMERA_W, 1), np.float32),
            "imu_accel":     spaces.Box(-50.0, 50.0, (3,), np.float32),
            "imu_gyro":      spaces.Box(-10.0, 10.0, (3,), np.float32),
            "pose_local":    spaces.Box(-np.inf, np.inf, (6,), np.float32),
            "goal_vector":   spaces.Box(-1.0, 1.0, (3,), np.float32),
            "wheel_speeds":  spaces.Box(-1.0, 1.0, (n_wheels,), np.float32),
        })
        self.action_space = spaces.Box(-1.0, 1.0, (2,), np.float32)

        self._sim = None  # IsaacSimManager injected at runtime

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        obs = self._get_obs()
        return obs, {}

    def step(self, action):
        # Send action → physics → get next obs
        obs = self._get_obs()
        reward = 0.0          # RewardComposer computed here
        terminated = False
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info

    def _get_obs(self):
        return {
            "lidar_ranges":  np.zeros(N_LIDAR_BEAMS, np.float32),
            "camera_depth":  np.zeros((CAMERA_H, CAMERA_W, 1), np.float32),
            "imu_accel":     np.zeros(3, np.float32),
            "imu_gyro":      np.zeros(3, np.float32),
            "pose_local":    np.zeros(6, np.float32),
            "goal_vector":   np.zeros(3, np.float32),
            "wheel_speeds":  np.zeros(6, np.float32),
        }

    def close(self):
        if self._sim:
            self._sim.stop()

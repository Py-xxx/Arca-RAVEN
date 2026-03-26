"""
Composite reward function.
Each component is independently weighted and logged to TensorBoard.
Weights are configurable per-scenario via configs/training/*.yaml.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class RewardWeights:
    progress:          float = 1.0    # forward movement toward goal
    tilt_penalty:      float = 2.0    # roll/pitch — tip-over risk
    slip_penalty:      float = 0.8    # wheel slip ratio — energy + terrain damage
    proximity_penalty: float = 1.5    # distance to nearest hazard (inverted)
    power_penalty:     float = 0.5    # total motor power draw
    lateral_accel:     float = 0.6    # lateral g-force — mechanical wear
    smoothness_bonus:  float = 0.3    # path curvature smoothness


class RewardComposer:
    def __init__(self, weights: RewardWeights | None = None):
        self.w = weights or RewardWeights()

    def compute(self, state: dict, prev_state: dict) -> tuple[float, dict]:
        """
        Returns (total_reward, component_dict) for logging.
        state keys: pose, imu_accel, imu_gyro, wheel_slip, motor_power,
                    goal_distance, nearest_hazard_dist, path_curvature
        """
        components = {}

        # Progress: reward proportional to reduction in goal distance
        d_goal = prev_state["goal_distance"] - state["goal_distance"]
        components["progress"] = self.w.progress * d_goal

        # Tilt penalty: penalise excessive roll/pitch
        roll, pitch = state["pose"][3], state["pose"][4]
        tilt = np.sqrt(roll**2 + pitch**2)
        components["tilt"] = -self.w.tilt_penalty * max(0.0, tilt - 0.1)

        # Wheel slip penalty
        slip = np.mean(state["wheel_slip"])
        components["slip"] = -self.w.slip_penalty * slip

        # Proximity penalty: zero within safe radius, grows as hazard approaches
        safe_dist = 1.0
        hazard_d = state["nearest_hazard_dist"]
        components["proximity"] = -self.w.proximity_penalty * max(0.0, safe_dist - hazard_d)

        # Power penalty: penalise high total motor draw
        components["power"] = -self.w.power_penalty * state["motor_power"]

        # Lateral acceleration penalty
        lat_g = abs(state["imu_accel"][1]) / 9.81
        components["lateral"] = -self.w.lateral_accel * lat_g

        # Smoothness bonus
        components["smooth"] = self.w.smoothness_bonus * (1.0 - state["path_curvature"])

        total = sum(components.values())
        return total, components

"""
Mock simulation for Arca RAVEN.
Generates realistic rover telemetry without Isaac Sim.
Used for frontend development on machines without an NVIDIA GPU.
"""

import math
import time
import random
from typing import Any


class MockSimulation:
    TERRAINS = {
        "mars": {
            "gravity": -3.72,
            "gps_lat": -4.5895,
            "gps_lon": 137.4417,
            "gps_alt": -4500.0,
            "description": "Gale Crater, Mars",
        },
        "moon": {
            "gravity": -1.62,
            "gps_lat": 0.6741,
            "gps_lon": 23.4733,
            "gps_alt": 0.0,
            "description": "Mare Tranquillitatis, Moon",
        },
        "asteroid": {
            "gravity": -0.003,
            "gps_lat": 0.0,
            "gps_lon": 0.0,
            "gps_alt": 0.0,
            "description": "433 Eros",
        },
        "earth": {
            "gravity": -9.81,
            "gps_lat": 35.3606,
            "gps_lon": -116.8895,
            "gps_alt": 900.0,
            "description": "Mojave Desert, California",
        },
    }

    ROVER_WHEEL_COUNTS = {
        "rocker_bogie": 6,
        "skid_steer": 4,
    }

    def __init__(self):
        self.t = 0.0
        self.terrain = "mars"
        self.rover_type = "rocker_bogie"
        self.episode = 0
        self.step = 0
        self.cumulative_reward = 0.0
        self.is_training = False
        self.speed = 0.08  # m/s — realistic for planetary rover (~0.08 m/s avg)

    def set_terrain(self, terrain: str):
        if terrain in self.TERRAINS:
            self.terrain = terrain
            self.t = 0.0

    def set_rover(self, rover_type: str):
        if rover_type in self.ROVER_WHEEL_COUNTS:
            self.rover_type = rover_type

    def set_training(self, active: bool):
        self.is_training = active
        if active and self.step == 0:
            self.episode = 1

    def _figure_eight(self, t: float, scale: float = 8.0):
        """Lemniscate of Bernoulli path."""
        denom = 1 + math.sin(t) ** 2
        x = scale * math.cos(t) / denom
        y = scale * math.sin(t) * math.cos(t) / denom
        dx = -scale * (math.sin(t) * denom - math.cos(t) * 2 * math.sin(t) * math.cos(t)) / denom**2
        dy = scale * ((math.cos(t)**2 - math.sin(t)**2) * denom - math.sin(t) * math.cos(t) * 2 * math.sin(t) * math.cos(t)) / denom**2
        yaw = math.atan2(dy, dx)
        return x, y, yaw

    def _lidar_ranges(self, x: float, y: float, num_rays: int = 360) -> list:
        """Simulate 360-degree Ouster OS1-64 style LiDAR returns."""
        ranges = []
        for i in range(num_rays):
            angle = (i / num_rays) * 2 * math.pi
            base = 10.0 + 5.0 * math.sin(x * 0.5 + angle * 2.1) + 3.0 * math.cos(y * 0.4 + angle * 3.7)
            noise = random.gauss(0, 0.03)
            ranges.append(round(max(0.3, min(50.0, base + noise)), 3))
        return ranges

    def tick(self) -> dict[str, Any]:
        td = self.TERRAINS[self.terrain]
        gravity = td["gravity"]

        x, y, yaw = self._figure_eight(self.t)
        z = 0.15  # rover ground clearance

        pitch = 0.04 * math.sin(self.t * 2.3 + 0.5)
        roll = 0.025 * math.cos(self.t * 1.7 + 1.2)

        speed = self.speed * (0.9 + 0.1 * random.random())
        wheel_count = self.ROVER_WHEEL_COUNTS.get(self.rover_type, 4)
        wheel_speeds = [round(speed + random.gauss(0, 0.003), 5) for _ in range(wheel_count)]

        accel = {
            "x": round(random.gauss(0, 0.015), 5),
            "y": round(random.gauss(0, 0.015), 5),
            "z": round(gravity + random.gauss(0, 0.04), 5),
        }
        gyro = {
            "x": round(random.gauss(0, 0.0008), 6),
            "y": round(random.gauss(0, 0.0008), 6),
            "z": round(random.gauss(0, 0.0008), 6),
        }

        meters_per_deg = 111320.0
        gps = {
            "latitude": round(td["gps_lat"] + y / meters_per_deg, 7),
            "longitude": round(td["gps_lon"] + x / (meters_per_deg * max(0.001, math.cos(math.radians(td["gps_lat"])))), 7),
            "altitude": round(td["gps_alt"] + z, 3),
        }

        reward = 0.0
        if self.is_training:
            self.step += 1
            reward = round(0.6 + 0.25 * math.sin(self.step * 0.008) + 0.15 * math.sin(self.step * 0.003) + random.gauss(0, 0.08), 5)
            self.cumulative_reward += reward
            if self.step % 500 == 0:
                self.episode += 1
                self.cumulative_reward = 0.0

        self.t += 0.02  # 20 Hz tick

        return {
            "type": "rover_state",
            "timestamp": time.time(),
            "rover": {
                "id": "raven-001",
                "type": self.rover_type,
                "position": {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4)},
                "orientation": {"roll": round(roll, 5), "pitch": round(pitch, 5), "yaw": round(yaw, 5)},
                "velocity": {"linear": round(speed, 5), "angular": round(abs(gyro["z"]), 6)},
                "wheel_speeds": wheel_speeds,
            },
            "sensors": {
                "imu": {"accelerometer": accel, "gyroscope": gyro},
                "lidar": {
                    "ranges": self._lidar_ranges(x, y),
                    "min_range": 0.3,
                    "max_range": 50.0,
                    "num_rays": 360,
                },
                "gps": gps,
            },
            "training": {
                "episode": self.episode,
                "step": self.step,
                "reward": reward,
                "cumulative_reward": round(self.cumulative_reward, 5),
                "is_training": self.is_training,
            },
            "environment": {
                "terrain": self.terrain,
                "gravity": gravity,
                "description": td["description"],
                "simulation_time": round(self.t, 4),
            },
        }

"""Shared terrain and rover catalog used by simulation backends."""

from __future__ import annotations

from typing import Final


DEFAULT_TERRAIN: Final[str] = "mars"
DEFAULT_ROVER_TYPE: Final[str] = "rocker_bogie"

TERRAINS: Final[dict[str, dict[str, float | str]]] = {
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

ROVER_WHEEL_COUNTS: Final[dict[str, int]] = {
    "rocker_bogie": 6,
    "skid_steer": 4,
}

"""Shared contract for simulation backends used by the bridge."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SimulationBackend(ABC):
    mode: str

    @property
    @abstractmethod
    def ready(self) -> bool:
        """Whether the backend can currently stream real state."""

    @abstractmethod
    def start(self) -> None:
        """Initialise the backend."""

    @abstractmethod
    def stop(self) -> None:
        """Tear down the backend."""

    @abstractmethod
    def tick(self) -> dict[str, Any] | None:
        """Advance the backend and return the latest rover state if available."""

    @abstractmethod
    def get_config(self) -> dict[str, Any]:
        """Return selectable frontend configuration."""

    @abstractmethod
    def get_health(self) -> dict[str, Any]:
        """Return backend-specific health information."""

    @abstractmethod
    def set_terrain(self, terrain: str) -> None:
        """Switch the active terrain if supported."""

    @abstractmethod
    def set_rover(self, rover_type: str) -> None:
        """Switch the active rover if supported."""

    @abstractmethod
    def set_training(self, active: bool) -> None:
        """Toggle training state if supported."""

    @abstractmethod
    def reset(self) -> None:
        """Reset simulation and training counters."""

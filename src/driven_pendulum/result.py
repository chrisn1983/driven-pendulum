"""Container for simulation output: raw time series plus derived physical quantities.

A :class:`SimulationResult` is what :meth:`driven_pendulum.model.DrivenPendulum.simulate`
returns.  It holds the raw integrator output (time, angle, angular velocity) and computes
derived quantities (Cartesian bob track, energy, pivot motion) lazily on request.  It also
exposes the data as a :class:`pandas.DataFrame` / CSV so results can be captured for downstream
use, satisfying the brief's "raw data" requirement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .parameters import PendulumParameters


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Immutable result of a single pendulum simulation.

    Attributes
    ----------
    t:
        Sample times in seconds, shape ``(N,)``.
    theta:
        Angle from the downward vertical in radians, shape ``(N,)``.
    theta_dot:
        Angular velocity in rad/s, shape ``(N,)``.
    parameters:
        The :class:`PendulumParameters` used to produce this result.
    initial_state:
        The ``(theta0, theta_dot0)`` initial condition, for provenance.
    """

    t: np.ndarray
    theta: np.ndarray
    theta_dot: np.ndarray
    parameters: PendulumParameters
    initial_state: tuple[float, float]

    # -- Derived kinematics ------------------------------------------------------------

    @property
    def theta_wrapped(self) -> np.ndarray:
        """Angle wrapped to the interval ``(-pi, pi]`` for tidy plotting."""
        return (self.theta + np.pi) % (2.0 * np.pi) - np.pi

    @property
    def pivot_x(self) -> np.ndarray:
        """Horizontal pivot position ``x_p(t) = A*sin(omega*t)`` in metres."""
        p = self.parameters
        return p.A * np.sin(p.omega * self.t)

    @property
    def pivot_velocity(self) -> np.ndarray:
        """Horizontal pivot velocity ``A*omega*cos(omega*t)`` in m/s."""
        p = self.parameters
        return p.A * p.omega * np.cos(p.omega * self.t)

    @property
    def bob_x(self) -> np.ndarray:
        """Horizontal bob position in metres (lab frame)."""
        return self.pivot_x + self.parameters.L * np.sin(self.theta)

    @property
    def bob_y(self) -> np.ndarray:
        """Vertical bob position in metres (lab frame), with the pivot at ``y = 0``."""
        return -self.parameters.L * np.cos(self.theta)

    # -- Energy ------------------------------------------------------------------------

    @property
    def kinetic_energy(self) -> np.ndarray:
        """Lab-frame kinetic energy of the bob in joules.

        Includes the contribution of the moving pivot, so for a driven pendulum this is *not*
        conserved (the drive does work).  For the undriven case (``A = 0``) it reduces to the
        usual ``0.5 m L^2 theta_dot^2``.
        """
        p = self.parameters
        x_dot = self.pivot_velocity + p.L * np.cos(self.theta) * self.theta_dot
        y_dot = p.L * np.sin(self.theta) * self.theta_dot
        return 0.5 * p.m * (x_dot**2 + y_dot**2)

    @property
    def potential_energy(self) -> np.ndarray:
        """Gravitational potential energy in joules, zero at the downward vertical."""
        p = self.parameters
        return p.m * p.g * p.L * (1.0 - np.cos(self.theta))

    @property
    def total_energy(self) -> np.ndarray:
        """Total mechanical energy ``KE + PE`` in joules.

        Conserved only in the conservative limit (``b = 0`` and ``A = 0``); otherwise damping
        removes energy and the drive injects it.
        """
        return self.kinetic_energy + self.potential_energy

    # -- Export ------------------------------------------------------------------------

    def to_dataframe(self) -> pd.DataFrame:
        """Return the raw and derived time series as a tidy :class:`pandas.DataFrame`."""
        return pd.DataFrame(
            {
                "t": self.t,
                "theta": self.theta,
                "theta_dot": self.theta_dot,
                "theta_wrapped": self.theta_wrapped,
                "pivot_x": self.pivot_x,
                "bob_x": self.bob_x,
                "bob_y": self.bob_y,
                "kinetic_energy": self.kinetic_energy,
                "potential_energy": self.potential_energy,
                "total_energy": self.total_energy,
            }
        )

    def to_csv(self, path: str | Path) -> Path:
        """Write the result to ``path`` as CSV and return the resolved path."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_csv(path, index=False)
        return path

    def to_dict(self) -> dict[str, np.ndarray]:
        """Return the raw arrays as a plain dictionary (no derived quantities)."""
        return {"t": self.t, "theta": self.theta, "theta_dot": self.theta_dot}

    def __len__(self) -> int:
        return int(self.t.size)

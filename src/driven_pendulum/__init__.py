"""Driven, damped pendulum: simulation and analysis.

A small, object-oriented toolkit for simulating a pendulum whose pivot is driven horizontally
(``x_p(t) = A*sin(omega*t)``) and exploring its behaviour.

Quick start
-----------
>>> from driven_pendulum import DrivenPendulum, PendulumParameters
>>> model = DrivenPendulum(PendulumParameters(A=0.5, omega=2.0))
>>> result = model.simulate(theta0=0.2, t_span=(0, 20))
>>> df = result.to_dataframe()
"""

from __future__ import annotations

from .analysis import (
    BifurcationResult,
    DivergenceResult,
    PoincareSection,
    ResonanceSweepResult,
    bifurcation_diagram,
    poincare_section,
    resonance_sweep,
    sensitivity_to_initial_conditions,
)
from .model import DrivenPendulum
from .parameters import PendulumParameters
from .result import SimulationResult

__all__ = [
    "PendulumParameters",
    "DrivenPendulum",
    "SimulationResult",
    "resonance_sweep",
    "ResonanceSweepResult",
    "poincare_section",
    "PoincareSection",
    "bifurcation_diagram",
    "BifurcationResult",
    "sensitivity_to_initial_conditions",
    "DivergenceResult",
]

__version__ = "0.1.0"

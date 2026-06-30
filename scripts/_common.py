"""Shared helpers and canonical parameter sets for the example scripts.

Run any script from the project root, e.g.::

    uv run python scripts/run_timeseries.py

Figures and CSVs are written to the ``outputs/`` directory.
"""

from __future__ import annotations

from pathlib import Path

from driven_pendulum import PendulumParameters

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

# Canonical parameter sets used across the scripts and the README.
# The brief's baseline damping b = 0.5 is kept throughout.
DRIVEN_REGULAR = PendulumParameters(b=0.5, A=0.5, omega=2.0)
CHAOTIC = PendulumParameters(b=0.5, A=2.5, omega=3.0)


def output_path(name: str) -> Path:
    """Return ``outputs/<name>``, creating the directory if needed."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR / name

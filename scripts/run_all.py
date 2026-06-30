"""Run every example script in sequence to regenerate all outputs."""

from __future__ import annotations

import run_animation
import run_bifurcation
import run_phase_portrait
import run_poincare
import run_resonance
import run_sensitivity
import run_timeseries


def main() -> None:
    for module in (
        run_timeseries,
        run_phase_portrait,
        run_resonance,
        run_poincare,
        run_sensitivity,
        run_bifurcation,
        run_animation,
    ):
        print(f"\n=== {module.__name__} ===")
        module.main()


if __name__ == "__main__":
    main()

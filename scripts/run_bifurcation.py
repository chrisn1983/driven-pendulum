"""Build a bifurcation diagram by sweeping the drive amplitude A.

Sweeping A at fixed omega reveals period-doubling and chaotic bands -- the route to chaos.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import output_path
from driven_pendulum import PendulumParameters, bifurcation_diagram
from driven_pendulum.plotting import plot_bifurcation


def main() -> None:
    base = PendulumParameters(b=0.5, omega=3.0)
    amplitudes = np.linspace(0.2, 3.0, 400)
    result = bifurcation_diagram(
        base, "A", amplitudes, theta0=0.2, n_periods=80, transient_periods=300
    )
    fig = plot_bifurcation(result, save_path=output_path("bifurcation_A.png"))
    plt.close(fig)
    print(f"bifurcation diagram ({len(amplitudes)} amplitudes) -> outputs/bifurcation_A.png")


if __name__ == "__main__":
    main()

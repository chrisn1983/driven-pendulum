"""Compute and plot a Poincaré section for the chaotic regime."""

from __future__ import annotations

import matplotlib.pyplot as plt

from _common import CHAOTIC, output_path
from driven_pendulum import poincare_section
from driven_pendulum.plotting import plot_poincare


def main() -> None:
    section = poincare_section(
        CHAOTIC, theta0=0.2, n_periods=4000, transient_periods=300
    )
    fig = plot_poincare(section, save_path=output_path("poincare_chaotic.png"))
    plt.close(fig)
    print(f"Poincaré section ({len(section.theta)} points) -> outputs/poincare_chaotic.png")
    print(f"  params: A={CHAOTIC.A}, omega={CHAOTIC.omega}, b={CHAOTIC.b}")


if __name__ == "__main__":
    main()

"""Save phase portraits (theta vs theta_dot) and energy plots for both regimes."""

from __future__ import annotations

import matplotlib.pyplot as plt

from _common import CHAOTIC, DRIVEN_REGULAR, output_path
from driven_pendulum import DrivenPendulum
from driven_pendulum.plotting import plot_energy, plot_phase_portrait


def main() -> None:
    for label, params in (("regular", DRIVEN_REGULAR), ("chaotic", CHAOTIC)):
        result = DrivenPendulum(params).simulate(
            theta0=0.2, t_span=(0, 120), n_points=12000
        )
        fig = plot_phase_portrait(
            result, save_path=output_path(f"phase_portrait_{label}.png")
        )
        plt.close(fig)
        fig = plot_energy(result, save_path=output_path(f"energy_{label}.png"))
        plt.close(fig)
        print(f"[{label}] phase portrait -> outputs/phase_portrait_{label}.png")
        print(f"[{label}] energy        -> outputs/energy_{label}.png")


if __name__ == "__main__":
    main()

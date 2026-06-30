"""Plot the divergence of two near-identical trajectories (chaos fingerprint)."""

from __future__ import annotations

import matplotlib.pyplot as plt

from _common import CHAOTIC, DRIVEN_REGULAR, output_path
from driven_pendulum import sensitivity_to_initial_conditions
from driven_pendulum.plotting import plot_divergence


def main() -> None:
    for label, params in (("regular", DRIVEN_REGULAR), ("chaotic", CHAOTIC)):
        result = sensitivity_to_initial_conditions(
            params, delta=1e-9, t_span=(0, 80), n_points=4000
        )
        fig = plot_divergence(result, save_path=output_path(f"sensitivity_{label}.png"))
        plt.close(fig)
        growth = result.separation[-1] / result.delta0
        print(f"[{label}] separation grew by factor {growth:.2e} -> outputs/sensitivity_{label}.png")


if __name__ == "__main__":
    main()

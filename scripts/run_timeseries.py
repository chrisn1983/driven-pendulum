"""Simulate the pendulum and save the time series as a figure and a CSV.

Shows two regimes side by side: a gently driven pendulum that settles into a regular
oscillation, and the chaotic set used elsewhere in the project.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

from _common import CHAOTIC, DRIVEN_REGULAR, output_path
from driven_pendulum import DrivenPendulum
from driven_pendulum.plotting import plot_time_series


def main() -> None:
    for label, params in (("regular", DRIVEN_REGULAR), ("chaotic", CHAOTIC)):
        result = DrivenPendulum(params).simulate(
            theta0=0.2, t_span=(0, 60), n_points=6000
        )
        fig = plot_time_series(result, save_path=output_path(f"timeseries_{label}.png"))
        plt.close(fig)
        csv_path = result.to_csv(output_path(f"timeseries_{label}.csv"))
        print(f"[{label}] params: A={params.A}, omega={params.omega}, b={params.b}")
        print(f"  figure -> outputs/timeseries_{label}.png")
        print(f"  data   -> {csv_path}")


if __name__ == "__main__":
    main()

"""Render an animated GIF of the pendulum swinging on its driven pivot."""

from __future__ import annotations

import matplotlib.pyplot as plt

from _common import CHAOTIC, output_path
from driven_pendulum import DrivenPendulum
from driven_pendulum.plotting import animate


def main() -> None:
    # A short, well-sampled run makes a smooth GIF.
    result = DrivenPendulum(CHAOTIC).simulate(theta0=0.2, t_span=(0, 20), n_points=1200)
    anim = animate(result, save_path=output_path("pendulum.gif"), fps=30, skip=1, trail=60)
    plt.close(anim._fig)
    print("animation -> outputs/pendulum.gif")


if __name__ == "__main__":
    main()

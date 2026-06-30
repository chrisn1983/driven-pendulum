"""Run a single simulation with parameters of your choosing and display/save the result.

Examples
--------
Pick your own amplitude and frequency, run for 60 s, and pop the plots on screen::

    uv run python scripts/run_custom.py --A 1.3 --omega 2.7 --t 60 --show

Let it choose random drive parameters for you (great for open exploration)::

    uv run python scripts/run_custom.py --random --t 60 --show

Just save to outputs/ without opening a window (drop --show)::

    uv run python scripts/run_custom.py --A 0.8 --omega 3.1 --t 60
"""

from __future__ import annotations

import argparse
import random

import matplotlib.pyplot as plt
import numpy as np

from _common import output_path
from driven_pendulum import DrivenPendulum, PendulumParameters
from driven_pendulum.plotting import plot_energy, plot_phase_portrait, plot_time_series


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run one driven-pendulum simulation.")
    p.add_argument("--A", type=float, default=1.0, help="drive amplitude (m)")
    p.add_argument("--omega", type=float, default=2.5, help="drive frequency (rad/s)")
    p.add_argument("--b", type=float, default=0.5, help="damping coefficient (1/s)")
    p.add_argument("--L", type=float, default=1.0, help="length (m)")
    p.add_argument("--g", type=float, default=9.81, help="gravity (m/s^2)")
    p.add_argument("--theta0", type=float, default=0.2, help="initial angle (rad)")
    p.add_argument("--theta-dot0", type=float, default=0.0, help="initial angular velocity (rad/s)")
    p.add_argument("--t", type=float, default=60.0, help="simulation end time (s)")
    p.add_argument("--n-points", type=int, default=6000, help="number of output samples")
    p.add_argument("--name", type=str, default="custom", help="basename for the output files")
    p.add_argument("--show", action="store_true", help="open the figures in a window")
    p.add_argument(
        "--random",
        action="store_true",
        help="ignore --A/--omega and pick random drive parameters",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    A, omega = args.A, args.omega
    if args.random:
        A = round(random.uniform(0.5, 3.0), 3)
        omega = round(random.uniform(1.0, 4.0), 3)

    params = PendulumParameters(L=args.L, g=args.g, b=args.b, A=A, omega=omega)
    model = DrivenPendulum(params)
    result = model.simulate(
        theta0=args.theta0,
        theta_dot0=args.theta_dot0,
        t_span=(0.0, args.t),
        n_points=args.n_points,
    )

    # A short summary of what happened.
    went_over_top = bool(np.any(np.abs(result.theta) > np.pi))
    energy = result.total_energy
    print("Parameters:")
    print(f"  A={A}  omega={omega} rad/s  b={params.b}  L={params.L}  g={params.g}")
    print(f"  natural frequency omega_0 = {params.natural_frequency:.3f} rad/s")
    print(f"  initial: theta0={args.theta0} rad, theta_dot0={args.theta_dot0} rad/s")
    print(f"  duration: {args.t} s over {args.n_points} samples")
    print("Result:")
    print(f"  max |theta|      = {np.max(np.abs(result.theta)):.3f} rad")
    print(f"  final theta      = {result.theta[-1]:.3f} rad")
    print(f"  energy range     = [{energy.min():.3f}, {energy.max():.3f}] J")
    print(f"  went over the top: {'yes' if went_over_top else 'no'}")

    # Always save; the figures also stay open if --show is given.
    ts_fig = plot_time_series(result, save_path=output_path(f"{args.name}_timeseries.png"))
    pp_fig = plot_phase_portrait(result, save_path=output_path(f"{args.name}_phase.png"))
    en_fig = plot_energy(result, save_path=output_path(f"{args.name}_energy.png"))
    csv_path = result.to_csv(output_path(f"{args.name}.csv"))
    print("Saved:")
    print(f"  outputs/{args.name}_timeseries.png")
    print(f"  outputs/{args.name}_phase.png")
    print(f"  outputs/{args.name}_energy.png")
    print(f"  {csv_path}")

    if args.show:
        plt.show()
    else:
        for fig in (ts_fig, pp_fig, en_fig):
            plt.close(fig)


if __name__ == "__main__":
    main()

"""Sweep the drive frequency and plot the resonance curve.

Demonstrates the resonance peak near the natural frequency omega_0 = sqrt(g/L), and how
heavier damping lowers and broadens it.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import output_path
from driven_pendulum import PendulumParameters, resonance_sweep
from driven_pendulum.plotting import plot_resonance_curve


def main() -> None:
    base = PendulumParameters(A=0.02)  # small drive keeps the response linear/oscillatory
    omega0 = base.natural_frequency
    omega_values = np.linspace(0.3 * omega0, 1.8 * omega0, 120)

    # Overlay several damping values on one figure.
    fig, ax = plt.subplots(figsize=(9, 5))
    for b in (0.2, 0.5, 1.0):
        sweep = resonance_sweep(base.with_updates(b=b), omega_values)
        ax.plot(sweep.omega, sweep.amplitude, lw=1.5, label=f"b = {b}")
    ax.axvline(omega0, color="grey", ls="--", lw=1.0, label=rf"$\omega_0={omega0:.2f}$")
    ax.set_xlabel(r"drive frequency $\omega$ (rad/s)")
    ax.set_ylabel("steady-state amplitude (rad)")
    ax.set_title("Resonance curves for varying damping")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path("resonance.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Also save the baseline (b=0.5) sweep data as CSV.
    baseline = resonance_sweep(base.with_updates(b=0.5), omega_values)
    import pandas as pd

    pd.DataFrame({"omega": baseline.omega, "amplitude": baseline.amplitude}).to_csv(
        output_path("resonance.csv"), index=False
    )
    print(f"resonance figure -> outputs/resonance.png")
    print(f"baseline peak near omega = {baseline.peak_frequency:.3f} rad/s (omega_0 = {omega0:.3f})")

    # Single-curve helper figure too.
    fig = plot_resonance_curve(baseline, save_path=output_path("resonance_baseline.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()

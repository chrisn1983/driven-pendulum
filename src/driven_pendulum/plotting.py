"""Matplotlib visualisations for simulations and analyses.

All plotting lives here so the rest of the library stays free of Matplotlib.  Each function
returns the :class:`matplotlib.figure.Figure` it created (and optionally saves it), so callers
can compose, display or further annotate the figures as they wish.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.figure import Figure

from .analysis import BifurcationResult, PoincareSection, ResonanceSweepResult
from .result import SimulationResult


def _save(fig: Figure, save_path: str | Path | None) -> Figure:
    """Save ``fig`` to ``save_path`` (creating parent dirs) if a path was given."""
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_time_series(
    result: SimulationResult, *, save_path: str | Path | None = None
) -> Figure:
    """Plot angle and angular velocity against time on stacked axes."""
    fig, (ax_theta, ax_omega) = plt.subplots(2, 1, sharex=True, figsize=(9, 6))

    ax_theta.plot(result.t, result.theta, color="tab:blue", lw=1.2)
    ax_theta.set_ylabel(r"$\theta$ (rad)")
    ax_theta.set_title("Angle vs time")
    ax_theta.grid(alpha=0.3)

    ax_omega.plot(result.t, result.theta_dot, color="tab:red", lw=1.2)
    ax_omega.set_ylabel(r"$\dot{\theta}$ (rad/s)")
    ax_omega.set_xlabel("time (s)")
    ax_omega.set_title("Angular velocity vs time")
    ax_omega.grid(alpha=0.3)

    fig.tight_layout()
    return _save(fig, save_path)


def plot_phase_portrait(
    result: SimulationResult, *, wrap: bool = True, save_path: str | Path | None = None
) -> Figure:
    """Plot the trajectory in the ``(theta, theta_dot)`` phase plane.

    Colour encodes time, so the transient-to-attractor evolution is visible.
    """
    theta = result.theta_wrapped if wrap else result.theta
    fig, ax = plt.subplots(figsize=(7, 6))
    points = ax.scatter(
        theta, result.theta_dot, c=result.t, cmap="viridis", s=3, linewidths=0
    )
    fig.colorbar(points, ax=ax, label="time (s)")
    ax.set_xlabel(r"$\theta$ (rad)" + (" (wrapped)" if wrap else ""))
    ax.set_ylabel(r"$\dot{\theta}$ (rad/s)")
    ax.set_title("Phase portrait")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _save(fig, save_path)


def plot_energy(
    result: SimulationResult, *, save_path: str | Path | None = None
) -> Figure:
    """Plot kinetic, potential and total energy against time."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(result.t, result.kinetic_energy, label="kinetic", lw=1.0)
    ax.plot(result.t, result.potential_energy, label="potential", lw=1.0)
    ax.plot(result.t, result.total_energy, label="total", lw=1.5, color="black")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("energy (J)")
    ax.set_title("Energy vs time")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _save(fig, save_path)


def plot_resonance_curve(
    result: ResonanceSweepResult, *, save_path: str | Path | None = None
) -> Figure:
    """Plot steady-state amplitude versus drive frequency, marking the natural frequency."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(result.omega, result.amplitude, color="tab:purple", lw=1.5)
    omega0 = result.base_parameters.natural_frequency
    ax.axvline(
        omega0, color="grey", ls="--", lw=1.0, label=rf"$\omega_0=\sqrt{{g/L}}={omega0:.2f}$"
    )
    ax.axvline(
        result.peak_frequency,
        color="tab:red",
        ls=":",
        lw=1.0,
        label=rf"peak $\omega={result.peak_frequency:.2f}$",
    )
    ax.set_xlabel(r"drive frequency $\omega$ (rad/s)")
    ax.set_ylabel("steady-state amplitude (rad)")
    ax.set_title("Resonance curve")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _save(fig, save_path)


def plot_poincare(
    section: PoincareSection, *, save_path: str | Path | None = None
) -> Figure:
    """Scatter the stroboscopic ``(theta, theta_dot)`` samples of a Poincaré section."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(section.theta, section.theta_dot, s=2, color="tab:blue", linewidths=0)
    ax.set_xlabel(r"$\theta$ (rad, wrapped)")
    ax.set_ylabel(r"$\dot{\theta}$ (rad/s)")
    ax.set_title(rf"Poincaré section ($\omega={section.parameters.omega:.2f}$ rad/s)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _save(fig, save_path)


def plot_bifurcation(
    result: BifurcationResult, *, save_path: str | Path | None = None
) -> Figure:
    """Scatter Poincaré angle samples against the swept parameter."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(result.param_value, result.theta, s=0.5, color="black", linewidths=0, alpha=0.5)
    ax.set_xlabel(f"{result.param_name}")
    ax.set_ylabel(r"$\theta$ at strobe (rad)")
    ax.set_title(f"Bifurcation diagram (sweeping {result.param_name})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _save(fig, save_path)


def plot_divergence(
    result, *, save_path: str | Path | None = None
) -> Figure:
    """Plot the phase-space separation of two nearby trajectories on a log scale."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(result.t, result.separation, color="tab:green", lw=1.0)
    ax.axhline(result.delta0, color="grey", ls="--", lw=1.0, label="initial separation")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("phase-space separation")
    ax.set_title("Sensitivity to initial conditions")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    return _save(fig, save_path)


def animate(
    result: SimulationResult,
    *,
    save_path: str | Path | None = None,
    fps: int = 30,
    skip: int = 1,
    trail: int = 40,
) -> FuncAnimation:
    """Animate the pendulum swinging on its horizontally driven pivot.

    Parameters
    ----------
    save_path:
        If given, the animation is written as a GIF via :class:`~matplotlib.animation.PillowWriter`
        (no external ffmpeg dependency).
    fps:
        Frames per second for the saved GIF.
    skip:
        Use every ``skip``-th sample as a frame (thins long simulations).
    trail:
        Number of recent bob positions to draw as a fading trail.
    """
    p = result.parameters
    frames = range(0, len(result), skip)

    pivot_x = result.pivot_x
    bob_x = result.bob_x
    bob_y = result.bob_y

    reach = p.A + p.L
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-reach * 1.1 - 0.1, reach * 1.1 + 0.1)
    ax.set_ylim(-p.L * 1.2, p.L * 0.4)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Driven pendulum")
    ax.grid(alpha=0.3)

    (rod,) = ax.plot([], [], "-", color="tab:gray", lw=2)
    (bob,) = ax.plot([], [], "o", color="tab:red", markersize=12)
    (pivot,) = ax.plot([], [], "s", color="black", markersize=8)
    (path,) = ax.plot([], [], "-", color="tab:red", lw=0.8, alpha=0.5)
    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    def init():
        rod.set_data([], [])
        bob.set_data([], [])
        pivot.set_data([], [])
        path.set_data([], [])
        time_text.set_text("")
        return rod, bob, pivot, path, time_text

    def update(i):
        rod.set_data([pivot_x[i], bob_x[i]], [0.0, bob_y[i]])
        bob.set_data([bob_x[i]], [bob_y[i]])
        pivot.set_data([pivot_x[i]], [0.0])
        start = max(0, i - trail * skip)
        path.set_data(bob_x[start : i + 1], bob_y[start : i + 1])
        time_text.set_text(f"t = {result.t[i]:.2f} s")
        return rod, bob, pivot, path, time_text

    anim = FuncAnimation(
        fig, update, frames=frames, init_func=init, blit=True, interval=1000 / fps
    )
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        anim.save(save_path, writer=PillowWriter(fps=fps))
    return anim

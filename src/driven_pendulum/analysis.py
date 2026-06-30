"""Higher-level exploration of the driven pendulum's behaviour.

These functions build on :class:`~driven_pendulum.model.DrivenPendulum` to probe the
qualitative dynamics the brief invites us to explore:

* :func:`resonance_sweep` -- steady-state amplitude versus drive frequency.
* :func:`poincare_section` -- stroboscopic sampling that distinguishes periodic from chaotic
  motion.
* :func:`bifurcation_diagram` -- Poincaré samples versus a swept parameter (the route to chaos).
* :func:`sensitivity_to_initial_conditions` -- divergence of two near-identical trajectories,
  the fingerprint of chaos.

Every routine integrates through :meth:`DrivenPendulum.equation_of_motion`, so the dynamics are
never re-implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .model import DrivenPendulum
from .parameters import PendulumParameters


def _integrate_at(
    model: DrivenPendulum,
    state0: tuple[float, float],
    t_eval: np.ndarray,
    *,
    method: str = "RK45",
    rtol: float = 1e-9,
    atol: float = 1e-9,
) -> np.ndarray:
    """Integrate ``model`` from ``state0`` and return ``y`` sampled at ``t_eval``.

    A thin wrapper around :func:`scipy.integrate.solve_ivp` that reuses the model's equation of
    motion.  Returns an array of shape ``(2, len(t_eval))`` -> ``[theta, theta_dot]``.
    """
    solution = solve_ivp(
        model.equation_of_motion,
        (float(t_eval[0]), float(t_eval[-1])),
        list(state0),
        method=method,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
    )
    if not solution.success:
        raise RuntimeError(f"Integration failed: {solution.message}")
    return solution.y


# ----------------------------------------------------------------------------------------
# Resonance
# ----------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ResonanceSweepResult:
    """Result of a frequency sweep.

    Attributes
    ----------
    omega:
        Drive frequencies tested (rad/s).
    amplitude:
        Steady-state angular amplitude at each frequency (rad), measured as half the
        peak-to-peak swing over the final measurement window.
    base_parameters:
        Parameters shared by every run (``omega`` is the swept quantity).
    """

    omega: np.ndarray
    amplitude: np.ndarray
    base_parameters: PendulumParameters

    @property
    def peak_frequency(self) -> float:
        """Drive frequency at which the steady-state amplitude is largest (rad/s)."""
        return float(self.omega[int(np.argmax(self.amplitude))])


def resonance_sweep(
    base_parameters: PendulumParameters,
    omega_values: np.ndarray,
    *,
    theta0: float = 0.05,
    settle_periods: int = 40,
    measure_periods: int = 20,
    points_per_period: int = 60,
) -> ResonanceSweepResult:
    """Sweep the drive frequency and record steady-state amplitude at each value.

    For every ``omega`` the system is integrated for ``settle_periods`` drive periods to let the
    transient decay, then the angular amplitude is measured over a further ``measure_periods``.
    The amplitude is reported as half the peak-to-peak swing of ``theta`` in that window.

    Notes
    -----
    Keep the drive amplitude ``A`` modest so the response stays oscillatory; a strong drive can
    push the pendulum over the top, at which point "amplitude" is no longer meaningful.
    """
    omega_values = np.asarray(omega_values, dtype=float)
    amplitudes = np.empty_like(omega_values)

    for i, omega in enumerate(omega_values):
        params = base_parameters.with_updates(omega=omega)
        model = DrivenPendulum(params)
        period = 2.0 * np.pi / omega
        total_periods = settle_periods + measure_periods
        n_points = total_periods * points_per_period
        t_eval = np.linspace(0.0, total_periods * period, n_points)
        y = _integrate_at(model, (theta0, 0.0), t_eval)

        measure_start = settle_periods * points_per_period
        theta_steady = y[0, measure_start:]
        amplitudes[i] = 0.5 * (theta_steady.max() - theta_steady.min())

    return ResonanceSweepResult(omega_values, amplitudes, base_parameters)


# ----------------------------------------------------------------------------------------
# Poincare sections
# ----------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PoincareSection:
    """Stroboscopic samples of the state, one per drive period.

    Attributes
    ----------
    theta:
        Angle samples, wrapped to ``(-pi, pi]`` (rad).
    theta_dot:
        Angular-velocity samples (rad/s).
    parameters:
        The parameters used.
    """

    theta: np.ndarray
    theta_dot: np.ndarray
    parameters: PendulumParameters


def poincare_section(
    parameters: PendulumParameters,
    *,
    theta0: float = 0.2,
    theta_dot0: float = 0.0,
    n_periods: int = 2000,
    transient_periods: int = 200,
    phase: float = 0.0,
) -> PoincareSection:
    """Sample the state once per drive period to build a Poincaré section.

    The state is recorded at times ``t_n = (phase + n) * T`` for ``T = 2*pi/omega``.  For
    periodic motion the section collapses to a few points; for chaotic motion it fills out a
    fractal-looking cloud.

    Parameters
    ----------
    transient_periods:
        Number of initial drive periods discarded before sampling.
    phase:
        Fractional offset (in periods) of the strobe within each drive cycle.
    """
    if parameters.omega <= 0:
        raise ValueError("Poincaré sections require a non-zero drive frequency.")

    model = DrivenPendulum(parameters)
    period = 2.0 * np.pi / parameters.omega
    n = np.arange(transient_periods, transient_periods + n_periods)
    t_eval = (phase + n) * period
    # solve_ivp needs t to start at t_span[0]; integrate from 0 through all strobe times.
    full_t_eval = np.concatenate(([0.0], t_eval))
    y = _integrate_at(model, (theta0, theta_dot0), full_t_eval)

    theta = y[0, 1:]
    theta_dot = y[1, 1:]
    theta_wrapped = (theta + np.pi) % (2.0 * np.pi) - np.pi
    return PoincareSection(theta_wrapped, theta_dot, parameters)


# ----------------------------------------------------------------------------------------
# Bifurcation diagram
# ----------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BifurcationResult:
    """Poincaré angle samples versus a swept parameter.

    ``param_value`` and ``theta`` are flat, equal-length arrays: each entry is one strobe
    sample plotted against the parameter value that produced it.
    """

    param_name: str
    param_value: np.ndarray
    theta: np.ndarray


def bifurcation_diagram(
    base_parameters: PendulumParameters,
    param_name: str,
    values: np.ndarray,
    *,
    theta0: float = 0.2,
    theta_dot0: float = 0.0,
    n_periods: int = 120,
    transient_periods: int = 200,
) -> BifurcationResult:
    """Build a bifurcation diagram by sweeping ``param_name`` over ``values``.

    For each value the steady-state Poincaré angles are collected; stacking them against the
    parameter reveals period-doubling cascades and chaotic bands.

    Parameters
    ----------
    param_name:
        Name of the :class:`PendulumParameters` field to sweep, typically ``"A"`` or ``"omega"``.
    """
    values = np.asarray(values, dtype=float)
    param_col: list[np.ndarray] = []
    theta_col: list[np.ndarray] = []

    for value in values:
        params = base_parameters.with_updates(**{param_name: value})
        section = poincare_section(
            params,
            theta0=theta0,
            theta_dot0=theta_dot0,
            n_periods=n_periods,
            transient_periods=transient_periods,
        )
        param_col.append(np.full(section.theta.shape, value))
        theta_col.append(section.theta)

    return BifurcationResult(
        param_name=param_name,
        param_value=np.concatenate(param_col),
        theta=np.concatenate(theta_col),
    )


# ----------------------------------------------------------------------------------------
# Sensitivity to initial conditions
# ----------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DivergenceResult:
    """Phase-space separation of two trajectories that start a hair apart.

    Attributes
    ----------
    t:
        Sample times (s).
    separation:
        Euclidean distance in ``(theta, theta_dot)`` space between the two runs at each time.
    delta0:
        The initial separation magnitude.
    """

    t: np.ndarray
    separation: np.ndarray
    delta0: float


def sensitivity_to_initial_conditions(
    parameters: PendulumParameters,
    *,
    theta0: float = 0.2,
    theta_dot0: float = 0.0,
    delta: float = 1e-8,
    t_span: tuple[float, float] = (0.0, 80.0),
    n_points: int = 4000,
) -> DivergenceResult:
    """Integrate two trajectories differing by ``delta`` in ``theta0`` and track their separation.

    In a chaotic regime the separation grows roughly exponentially (a positive Lyapunov
    exponent) until it saturates at the system's size; in a regular regime it stays bounded.
    """
    model = DrivenPendulum(parameters)
    t_eval = np.linspace(t_span[0], t_span[1], n_points)
    y_a = _integrate_at(model, (theta0, theta_dot0), t_eval)
    y_b = _integrate_at(model, (theta0 + delta, theta_dot0), t_eval)
    separation = np.sqrt((y_a[0] - y_b[0]) ** 2 + (y_a[1] - y_b[1]) ** 2)
    return DivergenceResult(t=t_eval, separation=separation, delta0=abs(delta))

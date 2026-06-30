"""The driven, damped pendulum model and its numerical integration.

:class:`DrivenPendulum` is the heart of the library.  It owns a set of
:class:`~driven_pendulum.parameters.PendulumParameters`, exposes the equation of motion as a
single method (the one source of truth reused by every script and test), and integrates the
system with :func:`scipy.integrate.solve_ivp`.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .parameters import PendulumParameters
from .result import SimulationResult


class DrivenPendulum:
    r"""A pendulum with a horizontally driven pivot.

    The state is ``[theta, theta_dot]`` and the equation of motion is

    .. math::

        \ddot\theta = -b\,\dot\theta - \frac{g}{L}\sin\theta
                       + \frac{A\,\omega^2}{L}\sin(\omega t)\cos\theta

    Parameters
    ----------
    parameters:
        The physical configuration.  Defaults to the brief's baseline (an *undriven* pendulum,
        ``A = omega = 0``); set ``A`` and ``omega`` to drive it.
    """

    def __init__(self, parameters: PendulumParameters | None = None) -> None:
        self.parameters = parameters if parameters is not None else PendulumParameters()

    def __repr__(self) -> str:
        return f"DrivenPendulum({self.parameters!r})"

    def with_parameters(self, **changes: float) -> "DrivenPendulum":
        """Return a new model with updated parameters (the original is untouched)."""
        return DrivenPendulum(self.parameters.with_updates(**changes))

    def equation_of_motion(self, t: float, state: np.ndarray) -> list[float]:
        """Return ``[theta_dot, theta_ddot]`` for the given time and state.

        This is written for the signature :func:`scipy.integrate.solve_ivp` expects,
        ``f(t, y)``, and is the single definition of the dynamics used everywhere.
        """
        p = self.parameters
        theta, theta_dot = state
        theta_ddot = (
            -p.b * theta_dot
            - (p.g / p.L) * np.sin(theta)
            + (p.A * p.omega**2 / p.L) * np.sin(p.omega * t) * np.cos(theta)
        )
        return [theta_dot, theta_ddot]

    def simulate(
        self,
        theta0: float = 0.2,
        theta_dot0: float = 0.0,
        *,
        t_span: tuple[float, float] = (0.0, 20.0),
        n_points: int = 2000,
        method: str = "RK45",
        rtol: float = 1e-9,
        atol: float = 1e-9,
        max_step: float | None = None,
    ) -> SimulationResult:
        """Integrate the equation of motion and return a :class:`SimulationResult`.

        Parameters
        ----------
        theta0, theta_dot0:
            Initial angle (rad) and angular velocity (rad/s).
        t_span:
            ``(t_start, t_end)`` integration interval in seconds.
        n_points:
            Number of uniformly spaced output samples across ``t_span``.
        method:
            Any ``solve_ivp`` method name.  ``"RK45"`` is a good default; ``"DOP853"`` is
            worthwhile for long chaotic runs where high accuracy matters.
        rtol, atol:
            Relative and absolute integration tolerances.  The tight defaults keep the
            conservative-limit energy drift small enough for the validation tests.
        max_step:
            Optional cap on the internal step size.  Useful for stiff/strongly driven runs to
            stop the adaptive stepper from striding over fast forcing oscillations.

        Raises
        ------
        RuntimeError
            If the integrator fails to converge.
        """
        t_start, t_end = t_span
        if t_end <= t_start:
            raise ValueError(f"t_span must be increasing, got {t_span}.")
        if n_points < 2:
            raise ValueError(f"n_points must be at least 2, got {n_points}.")

        t_eval = np.linspace(t_start, t_end, n_points)
        solver_kwargs: dict[str, object] = {
            "fun": self.equation_of_motion,
            "t_span": t_span,
            "y0": [theta0, theta_dot0],
            "method": method,
            "t_eval": t_eval,
            "rtol": rtol,
            "atol": atol,
            "dense_output": True,
        }
        if max_step is not None:
            solver_kwargs["max_step"] = max_step

        solution = solve_ivp(**solver_kwargs)
        if not solution.success:
            raise RuntimeError(f"Integration failed: {solution.message}")

        return SimulationResult(
            t=solution.t,
            theta=solution.y[0],
            theta_dot=solution.y[1],
            parameters=self.parameters,
            initial_state=(theta0, theta_dot0),
        )

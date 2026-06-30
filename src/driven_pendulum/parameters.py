"""Physical parameters for the driven, damped pendulum.

The :class:`PendulumParameters` dataclass is the single, validated container for every
physical quantity in the model.  It is intentionally immutable (``frozen=True``) so that a
set of parameters can be shared freely between a model, its results and any analysis without
the risk of one caller silently mutating another's configuration.  Use :meth:`with_updates`
to derive a modified copy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class PendulumParameters:
    r"""Parameters of a pendulum whose pivot is driven horizontally as ``x_p(t) = A*sin(w*t)``.

    The equation of motion (with ``theta`` measured from the downward vertical) is

    .. math::

        \ddot\theta + b\,\dot\theta + \frac{g}{L}\sin\theta
            = \frac{A\,\omega^2}{L}\sin(\omega t)\cos\theta

    Attributes
    ----------
    L:
        Pendulum length in metres (``> 0``).
    m:
        Bob mass in kilograms (``> 0``).  Does not appear in the equation of motion (it cancels
        for a point mass) but is retained for energy calculations and physical completeness.
    g:
        Gravitational acceleration in m/s^2 (``> 0``).
    b:
        Linear (viscous) damping coefficient in 1/s (``>= 0``).
    A:
        Horizontal drive amplitude of the pivot in metres (``>= 0``).
    omega:
        Angular drive frequency in rad/s (``>= 0``).
    """

    L: float = 1.0
    m: float = 1.0
    g: float = 9.81
    b: float = 0.5
    A: float = 0.0
    omega: float = 0.0

    def __post_init__(self) -> None:
        if self.L <= 0:
            raise ValueError(f"Length L must be positive, got {self.L}.")
        if self.m <= 0:
            raise ValueError(f"Mass m must be positive, got {self.m}.")
        if self.g <= 0:
            raise ValueError(f"Gravity g must be positive, got {self.g}.")
        if self.b < 0:
            raise ValueError(f"Damping b must be non-negative, got {self.b}.")
        if self.A < 0:
            raise ValueError(f"Drive amplitude A must be non-negative, got {self.A}.")
        if self.omega < 0:
            raise ValueError(f"Drive frequency omega must be non-negative, got {self.omega}.")

    @property
    def natural_frequency(self) -> float:
        r"""Small-oscillation natural angular frequency ``omega_0 = sqrt(g / L)`` in rad/s."""
        return math.sqrt(self.g / self.L)

    @property
    def natural_period(self) -> float:
        r"""Small-oscillation period ``T_0 = 2*pi*sqrt(L / g)`` in seconds."""
        return 2.0 * math.pi / self.natural_frequency

    @property
    def drive_period(self) -> float:
        r"""Period of the pivot drive ``T = 2*pi / omega`` in seconds (``inf`` if undriven)."""
        return math.inf if self.omega == 0 else 2.0 * math.pi / self.omega

    @property
    def drive_strength(self) -> float:
        r"""Peak angular drive acceleration ``A*omega^2 / L`` (the forcing prefactor) in 1/s^2."""
        return self.A * self.omega**2 / self.L

    def with_updates(self, **changes: float) -> "PendulumParameters":
        """Return a new :class:`PendulumParameters` with the given fields replaced.

        This is the supported way to "adjust" parameters: it never mutates the original, so a
        baseline configuration can be swept safely.

        Example
        -------
        >>> base = PendulumParameters()
        >>> driven = base.with_updates(A=0.5, omega=2.0)
        >>> base.A, driven.A
        (0.0, 0.5)
        """
        return replace(self, **changes)

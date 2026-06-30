"""Physics-validation tests for the DrivenPendulum model.

These check the simulator against analytically known behaviour: equilibrium, the small-angle
period, energy conservation in the conservative limit, and energy decay under damping.
"""

from __future__ import annotations

import numpy as np
import pytest

from driven_pendulum import DrivenPendulum, PendulumParameters


def test_equation_of_motion_hand_value():
    # At theta=0, theta_dot=0 the only term that can be non-zero is the drive*cos(theta).
    p = PendulumParameters(L=1.0, b=0.5, A=0.5, omega=2.0)
    model = DrivenPendulum(p)
    # t chosen so sin(omega t) = 1  ->  drive term = A*omega^2/L.
    t = (np.pi / 2) / p.omega
    theta_dot, theta_ddot = model.equation_of_motion(t, [0.0, 0.0])
    assert theta_dot == 0.0
    assert theta_ddot == pytest.approx(p.A * p.omega**2 / p.L)


def test_equilibrium_stays_at_rest():
    # Undriven, started exactly at the stable equilibrium -> never moves.
    model = DrivenPendulum(PendulumParameters(A=0.0))
    result = model.simulate(theta0=0.0, theta_dot0=0.0, t_span=(0, 10), n_points=500)
    assert np.allclose(result.theta, 0.0, atol=1e-9)
    assert np.allclose(result.theta_dot, 0.0, atol=1e-9)


def test_small_angle_period_matches_theory():
    # Undamped, undriven small oscillation: period ~ 2*pi*sqrt(L/g).
    p = PendulumParameters(b=0.0, A=0.0, L=1.0, g=9.81)
    model = DrivenPendulum(p)
    theta0 = 0.01  # small enough that sin(theta) ~ theta
    result = model.simulate(theta0=theta0, t_span=(0, 20), n_points=20000)

    # Measure the period from upward zero crossings of theta.
    theta = result.theta
    t = result.t
    crossings = np.where((theta[:-1] < 0) & (theta[1:] >= 0))[0]
    # Linear interpolation of each crossing time.
    cross_times = t[crossings] - theta[crossings] * (
        (t[crossings + 1] - t[crossings]) / (theta[crossings + 1] - theta[crossings])
    )
    measured_period = np.mean(np.diff(cross_times))
    assert measured_period == pytest.approx(p.natural_period, rel=1e-3)


def test_energy_conserved_in_conservative_limit():
    # b=0, A=0 -> total mechanical energy must be constant.
    p = PendulumParameters(b=0.0, A=0.0)
    model = DrivenPendulum(p)
    result = model.simulate(theta0=0.8, t_span=(0, 30), n_points=6000)
    energy = result.total_energy
    drift = (energy.max() - energy.min()) / energy.mean()
    assert drift < 1e-5


def test_damping_dissipates_energy_to_rest():
    # b>0, A=0 -> energy decreases monotonically and the pendulum settles at the bottom.
    p = PendulumParameters(b=0.5, A=0.0)
    model = DrivenPendulum(p)
    result = model.simulate(theta0=1.0, t_span=(0, 60), n_points=6000)
    energy = result.total_energy
    # Allow a tiny numerical tolerance on monotonic decrease.
    assert np.all(np.diff(energy) <= 1e-9)
    assert energy[-1] < energy[0]
    assert result.theta[-1] == pytest.approx(0.0, abs=1e-2)
    assert result.theta_dot[-1] == pytest.approx(0.0, abs=1e-2)


def test_with_parameters_returns_new_model():
    model = DrivenPendulum(PendulumParameters())
    driven = model.with_parameters(A=0.5, omega=2.0)
    assert model.parameters.A == 0.0
    assert driven.parameters.A == 0.5


def test_simulate_rejects_bad_arguments():
    model = DrivenPendulum()
    with pytest.raises(ValueError):
        model.simulate(t_span=(10, 0))
    with pytest.raises(ValueError):
        model.simulate(n_points=1)

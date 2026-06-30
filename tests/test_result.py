"""Tests for SimulationResult derived quantities and export."""

from __future__ import annotations

import numpy as np

from driven_pendulum import DrivenPendulum, PendulumParameters


def _result(**param_kwargs):
    model = DrivenPendulum(PendulumParameters(**param_kwargs))
    return model.simulate(theta0=0.3, t_span=(0, 5), n_points=200)


def test_dataframe_shape_and_columns():
    result = _result(A=0.5, omega=2.0)
    df = result.to_dataframe()
    assert len(df) == len(result) == 200
    expected = {
        "t",
        "theta",
        "theta_dot",
        "theta_wrapped",
        "pivot_x",
        "bob_x",
        "bob_y",
        "kinetic_energy",
        "potential_energy",
        "total_energy",
    }
    assert expected.issubset(df.columns)


def test_to_csv_roundtrip(tmp_path):
    result = _result(A=0.5, omega=2.0)
    path = result.to_csv(tmp_path / "sub" / "run.csv")
    assert path.exists()
    text = path.read_text()
    assert "theta" in text.splitlines()[0]


def test_theta_wrapped_within_range():
    # A large initial velocity makes the pendulum rotate, so theta grows unbounded.
    model = DrivenPendulum(PendulumParameters(b=0.0, A=0.0))
    result = model.simulate(theta0=0.0, theta_dot0=10.0, t_span=(0, 5), n_points=500)
    assert result.theta.max() > np.pi  # genuinely wound past pi
    assert np.all(result.theta_wrapped > -np.pi - 1e-12)
    assert np.all(result.theta_wrapped <= np.pi + 1e-12)


def test_pivot_position_matches_definition():
    p = PendulumParameters(A=0.5, omega=2.0)
    result = DrivenPendulum(p).simulate(theta0=0.1, t_span=(0, 5), n_points=200)
    np.testing.assert_allclose(result.pivot_x, p.A * np.sin(p.omega * result.t))


def test_undriven_kinetic_energy_formula():
    # With A=0 the pivot is fixed and KE = 0.5 m L^2 theta_dot^2.
    p = PendulumParameters(A=0.0, b=0.0)
    result = DrivenPendulum(p).simulate(theta0=0.5, t_span=(0, 5), n_points=300)
    expected = 0.5 * p.m * p.L**2 * result.theta_dot**2
    np.testing.assert_allclose(result.kinetic_energy, expected, rtol=1e-9)

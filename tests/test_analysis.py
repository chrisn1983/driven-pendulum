"""Tests for the analysis routines (resonance, Poincaré, bifurcation, sensitivity)."""

from __future__ import annotations

import numpy as np
import pytest

from driven_pendulum import (
    PendulumParameters,
    bifurcation_diagram,
    poincare_section,
    resonance_sweep,
    sensitivity_to_initial_conditions,
)


def test_resonance_peak_near_natural_frequency():
    # Light damping, small drive -> linear resonance peak close to omega_0 = sqrt(g/L).
    base = PendulumParameters(b=0.2, A=0.02)
    omega0 = base.natural_frequency
    omega_values = np.linspace(0.6 * omega0, 1.4 * omega0, 25)
    result = resonance_sweep(
        base, omega_values, settle_periods=30, measure_periods=15, points_per_period=40
    )
    assert result.peak_frequency == pytest.approx(omega0, rel=0.1)


def test_poincare_periodic_collapses_to_few_points():
    # A weak drive gives period-1 motion: every strobe lands at nearly the same point.
    params = PendulumParameters(b=0.5, A=0.05, omega=2.0)
    section = poincare_section(params, n_periods=80, transient_periods=120)
    assert np.ptp(section.theta) < 1e-2
    assert np.ptp(section.theta_dot) < 1e-2


def test_poincare_requires_drive():
    with pytest.raises(ValueError):
        poincare_section(PendulumParameters(omega=0.0))


def test_bifurcation_shapes_align():
    base = PendulumParameters(b=0.5, omega=2.0)
    values = np.linspace(0.5, 1.2, 6)
    result = bifurcation_diagram(
        base, "A", values, n_periods=20, transient_periods=40
    )
    assert result.param_value.shape == result.theta.shape
    assert result.param_name == "A"
    assert set(np.unique(result.param_value)).issubset(set(values))


def test_sensitivity_diverges_in_chaotic_regime():
    # A strongly driven pendulum is chaotic: tiny perturbations grow far beyond the seed.
    # (A=2.5, omega=3.0, b=0.5) is the canonical chaotic set used throughout the project.
    params = PendulumParameters(b=0.5, A=2.5, omega=3.0)
    result = sensitivity_to_initial_conditions(
        params, delta=1e-9, t_span=(0, 80), n_points=4000
    )
    assert result.separation[-1] > 1e6 * result.delta0

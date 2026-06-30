"""Tests for the PendulumParameters value object."""

from __future__ import annotations

import math

import pytest

from driven_pendulum import PendulumParameters


def test_defaults_match_brief_baseline():
    p = PendulumParameters()
    assert (p.L, p.m, p.g, p.b) == (1.0, 1.0, 9.81, 0.5)
    # Undriven by default.
    assert p.A == 0.0 and p.omega == 0.0


def test_natural_frequency_and_period():
    p = PendulumParameters(L=1.0, g=9.81)
    assert p.natural_frequency == pytest.approx(math.sqrt(9.81))
    assert p.natural_period == pytest.approx(2 * math.pi / math.sqrt(9.81))


def test_drive_strength():
    p = PendulumParameters(L=2.0, A=0.5, omega=3.0)
    assert p.drive_strength == pytest.approx(0.5 * 9.0 / 2.0)


def test_with_updates_is_non_mutating():
    base = PendulumParameters()
    driven = base.with_updates(A=0.5, omega=2.0)
    assert base.A == 0.0 and base.omega == 0.0
    assert driven.A == 0.5 and driven.omega == 2.0


def test_frozen_instance_cannot_be_mutated():
    p = PendulumParameters()
    with pytest.raises(Exception):
        p.L = 2.0  # type: ignore[misc]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"L": 0.0},
        {"L": -1.0},
        {"m": -1.0},
        {"g": 0.0},
        {"b": -0.1},
        {"A": -0.1},
        {"omega": -1.0},
    ],
)
def test_invalid_parameters_raise(kwargs):
    with pytest.raises(ValueError):
        PendulumParameters(**kwargs)

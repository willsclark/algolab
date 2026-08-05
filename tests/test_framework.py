"""Tests for the algolab framework itself: fitting, and the runner's
reproducibility / fairness / validation guarantees.
"""

from __future__ import annotations

import numpy as np
import pytest

import algolab as al


def test_fit_recovers_a_known_exponent_with_bracketing_ci():
    sizes = np.array([64, 128, 256, 512, 1024, 2048, 4096])
    values = 3.0 * sizes**2.0
    fit = al.fit_power_law(sizes, values, min_n=64, bootstrap=500)

    assert fit.exponent == pytest.approx(2.0, abs=1e-6)
    assert fit.coefficient == pytest.approx(3.0, rel=1e-6)
    assert fit.r_squared == pytest.approx(1.0, abs=1e-9)
    lo, hi = fit.exponent_ci
    assert lo <= 2.0 <= hi  # CI brackets the true exponent


def _identity_experiment(**overrides):
    # Two variants that each report the size of their input; inputs depend only
    # on (condition, size, trial) so both variants must see identical inputs.
    def generate(condition, size, rng):
        return [rng.random() for _ in range(size)]

    def measure(_payload, data):
        return {"total": float(sum(data))}

    cfg = dict(
        name="t",
        variants={"a": None, "b": None},
        metrics=["total"],
        run_trial=al.shared_input_trial(generate, measure),
        sizes=[8, 16, 32],
        conditions=["default"],
        n_trials=4,
        seed=99,
    )
    cfg.update(overrides)
    return al.Experiment(**cfg)


def test_runner_is_reproducible():
    r1 = al.run_experiment(_identity_experiment())
    r2 = al.run_experiment(_identity_experiment())
    assert r1.series("a", "default", "total") == r2.series("a", "default", "total")


def test_variants_see_identical_inputs():
    result = al.run_experiment(_identity_experiment())
    # Same seed per cell regardless of variant -> identical measured totals.
    assert result.series("a", "default", "total") == result.series("b", "default", "total")


def test_wrong_metrics_raise():
    def bad_trial(_payload, _condition, _size, _rng):
        return {"unexpected": 1.0}

    exp = _identity_experiment(run_trial=bad_trial)
    with pytest.raises(ValueError, match="expected"):
        al.run_experiment(exp)

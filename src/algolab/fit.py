"""Empirical complexity estimation.

Fit a power law ``y = c * n**k`` to (size, value) measurements by ordinary
least squares in log-log space. The exponent ``k`` is the empirical growth
rate; comparing it to a theoretical bound is the point of the exercise.

Optionally attach a bootstrap confidence interval on the exponent: resample the
fitted points with replacement, refit, and read percentiles off the resulting
distribution of slopes. A tight interval that brackets the theoretical exponent
is strong evidence the empirical and theoretical rates agree.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class PowerLawFit:
    """Result of fitting ``y = c * n**exponent`` in log-log space."""

    exponent: float
    coefficient: float
    r_squared: float
    n_points: int
    exponent_ci: tuple[float, float] | None = None  # bootstrap CI on the exponent

    def predict(self, sizes: np.ndarray) -> np.ndarray:
        return self.coefficient * np.asarray(sizes, dtype=float) ** self.exponent

    @property
    def label(self) -> str:
        base = f"~ n^{self.exponent:.3f}"
        if self.exponent_ci is not None:
            lo, hi = self.exponent_ci
            base += f" [{lo:.3f}, {hi:.3f}]"
        return f"{base}  (R²={self.r_squared:.3f})"


def _nan_fit(n_points: int) -> PowerLawFit:
    return PowerLawFit(float("nan"), float("nan"), float("nan"), n_points)


def _ols_slope(log_n: np.ndarray, log_y: np.ndarray) -> tuple[float, float]:
    """Slope and intercept of the least-squares line, via the covariance form.

    Equivalent to a degree-1 ``polyfit`` but numerically stable and warning-free
    even on the degenerate point sets bootstrap resampling can produce.
    """
    x_mean = log_n.mean()
    y_mean = log_y.mean()
    var_x = float(np.sum((log_n - x_mean) ** 2))
    if var_x == 0.0:
        return float("nan"), float("nan")
    slope = float(np.sum((log_n - x_mean) * (log_y - y_mean)) / var_x)
    intercept = float(y_mean - slope * x_mean)
    return slope, intercept


def _bootstrap_ci(
    log_n: np.ndarray,
    log_y: np.ndarray,
    n_resamples: int,
    ci: float,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = log_n.size
    slopes = np.empty(n_resamples)
    for i in range(n_resamples):
        idx = rng.integers(0, n, n)
        slopes[i] = _ols_slope(log_n[idx], log_y[idx])[0]
    # Degenerate resamples (all points sharing an x) yield nan slopes; ignore them.
    lo = float(np.nanpercentile(slopes, 100 * (1 - ci) / 2))
    hi = float(np.nanpercentile(slopes, 100 * (1 + ci) / 2))
    return lo, hi


def fit_power_law(
    sizes: npt.ArrayLike,
    values: npt.ArrayLike,
    min_n: int = 128,
    *,
    bootstrap: int = 0,
    ci: float = 0.95,
    seed: int = 0,
) -> PowerLawFit:
    """Fit a power law to ``(sizes, values)`` via log-log OLS.

    ``min_n`` drops the smallest inputs, where fixed overheads dominate and the
    asymptotic trend hasn't taken hold, biasing the exponent. Pass
    ``bootstrap=B`` (e.g. 1000) to attach a ``ci``-level confidence interval on
    the exponent; ``seed`` makes that interval reproducible.
    """
    sizes = np.asarray(sizes, dtype=float)
    values = np.asarray(values, dtype=float)

    mask = (sizes >= min_n) & (values > 0)
    if mask.sum() < 2:
        return _nan_fit(int(mask.sum()))

    log_n = np.log2(sizes[mask])
    log_y = np.log2(values[mask])
    slope, intercept = _ols_slope(log_n, log_y)

    predicted = slope * log_n + intercept
    ss_res = float(np.sum((log_y - predicted) ** 2))
    ss_tot = float(np.sum((log_y - log_y.mean()) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    exponent_ci = None
    if bootstrap > 0:
        exponent_ci = _bootstrap_ci(log_n, log_y, bootstrap, ci, seed)

    return PowerLawFit(
        exponent=slope,
        coefficient=float(2.0**intercept),
        r_squared=r_squared,
        n_points=int(mask.sum()),
        exponent_ci=exponent_ci,
    )

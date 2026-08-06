"""Turning a result grid into a table of fitted complexities."""

from __future__ import annotations

from dataclasses import dataclass

from algolab.fit import fit_power_law
from algolab.results import ExperimentResult


@dataclass(frozen=True)
class FitRow:
    variant: str
    condition: str
    metric: str
    exponent: float
    ci_low: float
    ci_high: float
    r_squared: float


def fit_table(
    result: ExperimentResult,
    metric: str,
    *,
    stat: str = "median",
    min_n: int = 128,
    bootstrap: int = 1000,
    seed: int = 0,
) -> list[FitRow]:
    """Fit ``metric`` vs. size for every (variant, condition) curve."""
    rows: list[FitRow] = []
    for variant in result.variants:
        for condition in result.conditions:
            sizes, values = result.series(variant, condition, metric, stat)
            fit = fit_power_law(sizes, values, min_n=min_n, bootstrap=bootstrap, seed=seed)
            lo, hi = fit.exponent_ci or (float("nan"), float("nan"))
            rows.append(
                FitRow(
                    variant=variant,
                    condition=condition,
                    metric=metric,
                    exponent=fit.exponent,
                    ci_low=lo,
                    ci_high=hi,
                    r_squared=fit.r_squared,
                )
            )
    return rows


def format_fit_table(rows: list[FitRow]) -> str:
    """Render :func:`fit_table` output as a fixed-width text table."""
    header = f"{'variant':<20} {'condition':<16} {'exponent':>10} {'95% CI':>18} {'R²':>7}"
    lines = [header, "-" * len(header)]
    for r in rows:
        ci = f"[{r.ci_low:.3f}, {r.ci_high:.3f}]"
        lines.append(
            f"{r.variant:<20} {r.condition:<16} {r.exponent:>10.3f} {ci:>18} {r.r_squared:>7.3f}"
        )
    return "\n".join(lines)

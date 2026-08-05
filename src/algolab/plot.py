"""Log-log plotting shared by every study.

The primitive :func:`loglog_fit_plot` takes named series ``{label: (sizes,
values)}`` and overlays a power-law best-fit (with fitted exponent and R²) on
the raw points. :func:`plot_experiment` is the convenience wrapper that pulls
those series straight out of an :class:`~algolab.results.ExperimentResult`.
Base-2 axes line up with the ``16, 32, 64, ...`` doubling schedule.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from algolab.fit import fit_power_law
from algolab.results import ExperimentResult

# Distinct marker+color pairs so series stay legible in black & white too.
_STYLES: Sequence[tuple[str, str]] = [
    ("o", "tab:blue"),
    ("s", "tab:green"),
    ("^", "tab:orange"),
    ("D", "tab:red"),
    ("v", "tab:purple"),
    ("P", "tab:brown"),
]

Series = tuple[Sequence[float], Sequence[float]]


def loglog_fit_plot(
    series: Mapping[str, Series],
    *,
    title: str = "",
    xlabel: str = "Input size (n)",
    ylabel: str = "Cost",
    fit_min_n: int = 128,
    bootstrap: int = 0,
    figsize: tuple[int, int] = (8, 6),
) -> Figure:
    """Scatter each series on log-log axes and overlay its power-law fit."""
    fig, ax = plt.subplots(figsize=figsize)

    styled = zip(series.items(), (_STYLES[i % len(_STYLES)] for i in range(len(series))))
    for (label, (sizes, values)), (marker, color) in styled:
        sizes_arr = np.asarray(sizes, dtype=float)
        values_arr = np.asarray(values, dtype=float)
        if sizes_arr.size == 0:
            continue

        ax.scatter(sizes_arr, values_arr, marker=marker, color=color, s=40, zorder=3)

        fit = fit_power_law(sizes_arr, values_arr, min_n=fit_min_n, bootstrap=bootstrap)
        n_line = np.logspace(
            np.log2(sizes_arr.min()), np.log2(sizes_arr.max()), 100, base=2
        )
        ax.plot(
            n_line,
            fit.predict(n_line),
            color=color,
            linestyle="--",
            zorder=2,
            label=f"{label.replace('_', ' ')} {fit.label}",
        )

    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    return fig


def plot_experiment(
    result: ExperimentResult,
    variant: str,
    metric: str,
    *,
    stat: str = "median",
    **kwargs,
) -> Figure:
    """Plot one variant's ``metric`` across all conditions, with fits."""
    series = {
        condition: result.series(variant, condition, metric, stat)
        for condition in result.conditions
    }
    kwargs.setdefault("title", f"{result.name}: {variant} — {metric}")
    kwargs.setdefault("ylabel", metric)
    return loglog_fit_plot(series, **kwargs)

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.figure import Figure

from src.analysis import BPStats


def load_stats(path: Path) -> BPStats:
    return BPStats.model_validate_json(path.read_text())


def stats_to_df(stats: BPStats) -> pd.DataFrame:
    rows = [
        {
            "sort": stats.algorithm.value,
            "size": input_size,
            "waste": waste,
        }
        for input_size, tg in stats.benchmarks.items()
        for waste in tg.trials.values()
    ]
    return pd.DataFrame(rows)


def fit_power_law(
    sizes: npt.NDArray, values: npt.NDArray, min_n: int = 128
) -> tuple[float, float, float]:
    """ """
    mask = sizes >= min_n
    if mask.sum() < 2:
        return float("nan"), float("nan"), float("nan")
    log_n = np.log2(sizes[mask])
    log_y = np.log2(values[mask])
    slope, intercept = np.polyfit(log_n, log_y, 1)
    # R² of the log-log fit
    predicted = slope * log_n + intercept
    ss_res = np.sum((log_y - predicted) ** 2)
    ss_tot = np.sum((log_y - log_y.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return slope, intercept, r_squared


def createfig(stats: BPStats) -> Figure:
    """Graphs sequence waste W(n) vs. size (n) on log-log axes."""
    df = stats_to_df(stats)

    fig, ax = plt.subplots()
    ax.set_title(f"{stats.algorithm.display_name}: Waste $W(n)$ vs. Input Size ($n$)")
    ax.set_xlabel("Input size $n$")
    ax.set_ylabel("Waste $W(n)$")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)

    # Raw trial scatter
    ax.scatter(df["size"], df["waste"], alpha=0.3, s=15, label="trials")

    # Mean per size for the fit + a cleaner overlay
    agg = df.groupby("size")["waste"].mean().reset_index()
    sizes = agg["size"].to_numpy()
    means = agg["waste"].to_numpy()
    ax.plot(sizes, means, "o-", color="black", label="mean", markersize=4)

    # Power-law fit on the means
    slope, intercept, r2 = fit_power_law(sizes, means)
    if np.isfinite(slope):
        fit_x = sizes[sizes >= 128]
        fit_y = 2 ** (slope * np.log2(fit_x) + intercept)
        ax.plot(
            fit_x,
            fit_y,
            "--",
            color="crimson",
            label=rf"fit: $W \sim n^{{{slope:.2f}}}$, $R^2={r2:.3f}$",
        )

    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    return fig

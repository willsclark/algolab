import pandas as pd
import numpy as np
from pathlib import Path
from math import log2, e
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from sklearn.metrics import r2_score
from models import AlgoStats, PermutationType

class Metric(Enum):
    TIME = "average_time"
    CMPS = "average_comparisons"

def load_stats(path: Path) -> AlgoStats:
    return AlgoStats.model_validate_json(path.read_text())


def stats_to_df(stats: AlgoStats) -> pd.DataFrame:
    rows = [
        {
            "sort": stats.sort.value,
            "permutation": perm_type.value,
            "size": size,
            "average_time": tg.average.time,
            "average_comparisons": tg.average.comparisons,
        }
        for perm_type, benchmark in stats.benchmarks.items()
        for size, tg in benchmark.benchmark.items()
    ]
    return pd.DataFrame(rows)



def fit_power_law(sizes: np.ndarray, values: np.ndarray, min_n: int = 128) -> tuple[float, float, float]:
    """
    """
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


def plot_sort_vs_perms(
    stats: AlgoStats,
    metric: Metric = Metric.TIME,
    fit_min_n: int = 16,
) -> Figure:
    """
    Plots one sort across all three permutation types on a log-log scale.
    metric: 'average_time' or 'average_comparisons'
    """
    df = stats_to_df(stats)
    sort_name = stats.sort.value

    fig, ax = plt.subplots(figsize=(8, 6))

    # Distinct colors + markers per permutation type so it's readable in B&W too
    styles = {
        PermutationType.UNIFORM.value: ("o", "tab:blue"),
        PermutationType.NEAR_SORTED.value: ("s", "tab:green"),
        PermutationType.TWO_ALTERNATING.value: ("^", "tab:orange"),
    }

    for perm_name, (marker, color) in styles.items():
        sub = df[df["permutation"] == perm_name]
        if sub.empty:
            continue
        sizes = sub["size"].to_numpy()
        values = sub[metric.value].to_numpy()
        m, b, r2 = fit_power_law(sizes, values, min_n=fit_min_n)

        # Scatter the raw measurements
        ax.scatter(sizes, values, marker=marker, color=color, s=40, zorder=3)

        # Overlay the best-fit line
        n_line = np.logspace(np.log2(sizes.min()), np.log2(sizes.max()), 100, base=2)
        y_line = (2.0 ** b) * (n_line ** m)
        label = f"{perm_name.replace('_', ' ')} ~ {m:.4f} log n + {b:.4f}, R²={r2:.4f}"
        ax.plot(n_line, y_line, color=color, linestyle="--", label=label, zorder=2)

    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("Input size (n, # of elements)")
    ax.set_ylabel("Time (s)" if metric == Metric.TIME else "Comparisons")
    ax.set_title(f"{sort_name}: {metric.value.replace('_', ' ')} vs. input size")
    ax.legend(loc="upper left", fontsize=9)

    fig.tight_layout()

    return fig




"""plot.py handles the plotting of NetworkStats objects"""

import matplotlib.pyplot as plt
import numpy as np

from network_stats import Property, TrialGroup
from output_manager import OutputManager, create_out_dir


def _analyze_scalar_growth(
    prop: Property, n_vals: np.ndarray, avg_vals: np.ndarray
) -> None:
    log_n = np.log2(n_vals)
    a, b = np.polyfit(log_n, avg_vals, 1)

    print(f"\n--- {prop.name} Growth Analysis ---")
    for n, v in zip(n_vals.astype(int), avg_vals):
        print(f"  n={n:>7,}: avg = {v:.4f}")

    ratio = avg_vals[-1] / avg_vals[0] if avg_vals[0] != 0 else float("inf")
    log_n_ratio = np.log2(n_vals[-1]) / np.log2(n_vals[0])

    print(f"  Value ratio (n=100k / n=1k):  {ratio:.4f}")
    print(f"  log(n) ratio (n=100k / n=1k): {log_n_ratio:.4f}")
    print(f"  Linear fit in log(n): y ≈ {a:.4f}·log(n) + {b:.4f}")

    if abs(ratio - 1.0) < 0.15:
        trend = "remains approximately constant as n grows"
    elif ratio > 1.0:
        pct_of_log = ratio / log_n_ratio
        if 0.85 < pct_of_log < 1.15:
            trend = f"increases, proportional to log(n)  (ratio={ratio:.3f} ≈ log(n) ratio={log_n_ratio:.3f})"
        elif pct_of_log >= 1.15:
            trend = f"increases faster than log(n)  (ratio={ratio:.3f} >> log(n) ratio={log_n_ratio:.3f})"
        else:
            trend = f"increases slower than log(n)  (ratio={ratio:.3f} << log(n) ratio={log_n_ratio:.3f})"
    else:
        trend = f"decreases as n grows  (ratio={ratio:.3f})"

    print(f"  Conclusion: {prop.name} {trend}")


def plot_scalar_vs_n(benchmarks: dict[Property, dict[int, TrialGroup]]) -> None:
    for prop, bench in benchmarks.items():
        n_vals = np.array(sorted(bench.keys()), dtype=float)
        avg_vals = np.array([bench[int(n)].average for n in sorted(bench.keys())])

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.semilogx(n_vals, avg_vals, "o-", label=f"Avg {prop.name.lower()}")

        log_n = np.log2(n_vals)
        if log_n[0] != 0:
            ref = 1.0 / log_n if prop == Property.CLUSTERING else log_n
            scale = avg_vals[0] / ref[0]
            ax.semilogx(n_vals, scale * ref, "--", color="gray", label="log(n) ref")

        ax.set_xlabel("n (log scale)")
        ax.set_ylabel(prop.name.replace("_", " ").title())
        ax.set_title(f"Avg {prop.name.replace('_', ' ').title()} vs n  (Lin-Log Scale)")
        ax.legend()
        fig.tight_layout()

        out_dir = create_out_dir(prop.value)
        OutputManager(out_dir).save_graph([fig])

        _analyze_scalar_growth(prop, n_vals, avg_vals)


def plot_degree_distributions(dists: dict[int, dict[int, int]]) -> None:
    out_dir = create_out_dir(Property.DEGREE_DIST.value)
    figures = []

    for n, dist in dists.items():
        degrees = sorted(dist.keys())
        counts = [dist[d] for d in degrees]

        fig_lin, ax_lin = plt.subplots(figsize=(8, 5))
        ax_lin.bar(degrees, counts, width=0.8, color="steelblue", alpha=0.8)
        ax_lin.set_xlabel("Degree k")
        ax_lin.set_ylabel("Number of vertices")
        ax_lin.set_title(f"Degree Distribution  n={n:,}  (Lin-Lin Scale)")
        fig_lin.tight_layout()
        figures.append(fig_lin)

        pos_deg = [d for d in degrees if d > 0 and dist[d] > 0]
        pos_cnt = [dist[d] for d in pos_deg]

        fig_log, ax_log = plt.subplots(figsize=(8, 5))
        ax_log.loglog(
            pos_deg, pos_cnt, "o", markersize=4, color="steelblue", label="data"
        )

        slope = None
        if len(pos_deg) > 2:
            log_k = np.log2(pos_deg)
            log_c = np.log2(pos_cnt)
            coeffs = np.polyfit(log_k, log_c, 1)
            slope, intercept = float(coeffs[0]), float(coeffs[1])
            fit_x = np.array([min(pos_deg), max(pos_deg)], dtype=float)
            fit_y = 2 ** (intercept + slope * np.log2(fit_x))
            ax_log.loglog(
                fit_x, fit_y, "--", color="red", label=f"fit: slope = {slope:.2f}"
            )

        ax_log.set_xlabel("Degree k (log scale)")
        ax_log.set_ylabel("Count (log scale)")
        ax_log.set_title(f"Degree Distribution  n={n:,}  (Log-Log Scale)")
        ax_log.legend()
        fig_log.tight_layout()
        figures.append(fig_log)

        print(f"\n--- Degree Distribution (n={n:,}) ---")
        if slope is not None:
            print(f"  Log-log slope: {slope:.4f}")
            if slope < -1:
                print(f"  Power law detected: P(k) ∝ k^({slope:.2f})")
                print(f"  Exponent: {slope:.4f}")
            else:
                print("  Slope does not clearly indicate a power law (|slope| < 1)")

    OutputManager(out_dir).save_graph(figures)

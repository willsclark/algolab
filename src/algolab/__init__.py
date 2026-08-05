"""algolab — a small framework for empirical algorithm analysis.

A study defines a ``run_trial`` and an :class:`Experiment`; the framework runs
the trials, aggregates them, fits empirical complexities with bootstrap
confidence intervals, and plots and stores the results.
"""

from algolab.analysis import FitRow, fit_table, format_fit_table
from algolab.experiment import (
    Experiment,
    Registry,
    run_experiment,
    shared_input_trial,
)
from algolab.fit import PowerLawFit, fit_power_law
from algolab.measure import Timing, time_call
from algolab.plot import loglog_fit_plot, plot_experiment
from algolab.results import Aggregate, Cell, ExperimentResult
from algolab.storage import (
    OutputError,
    load_result,
    output_dir,
    save_figure,
    save_result,
)

__all__ = [
    "Aggregate",
    "Cell",
    "Experiment",
    "ExperimentResult",
    "FitRow",
    "OutputError",
    "PowerLawFit",
    "Registry",
    "Timing",
    "fit_power_law",
    "fit_table",
    "format_fit_table",
    "load_result",
    "loglog_fit_plot",
    "output_dir",
    "plot_experiment",
    "run_experiment",
    "save_figure",
    "save_result",
    "shared_input_trial",
    "time_call",
]

"""Reading and writing experiment artifacts."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.pyplot import close

from algolab.results import ExperimentResult


class OutputError(Exception):
    pass


def output_dir(root: Path, name: str) -> Path:
    """Return (creating if needed) ``root/output/name``."""
    out = root / "output" / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_result(result: ExperimentResult, path: Path) -> None:
    """Write an :class:`ExperimentResult` to ``path`` as indented JSON."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result.model_dump_json(indent=2))
    except OSError as e:
        msg = f"failed to write result to {path}"
        raise OutputError(msg) from e


def load_result(path: Path) -> ExperimentResult:
    """Read an :class:`ExperimentResult` back from JSON."""
    try:
        return ExperimentResult.model_validate_json(path.read_text())
    except OSError as e:
        msg = f"failed to read result from {path}"
        raise OutputError(msg) from e


def save_figure(fig: Figure, path: Path) -> None:
    """Save and close a Matplotlib figure."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)
    except OSError as e:
        msg = f"failed to write figure to {path}"
        raise OutputError(msg) from e
    finally:
        close(fig)

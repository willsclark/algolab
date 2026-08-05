from enum import Enum
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.pyplot import close

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
JSON = "json"
PNG = "png"


class OutputError(Exception):
    pass


class DirType(Enum):
    STATS = "stats"
    GRAPHS = "graph_cmp"


def create_out_dir(algo: str) -> Path:
    """
    Creats a directory at output/algo/type
    """
    out_dir = PROJECT_ROOT / "output" / algo
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


class OutputManager:
    def __init__(self, out_dir: Path) -> None:
        self._out_dir = out_dir

    def save_stats(self, stats) -> None:
        """Saves a list of stats into a .JSON file
        following the AlgoStats JSON structure.

        STORAGE_DIR : ../output/algo/stats.json
        """
        stats_path = self._out_dir / f"{DirType.STATS.value}.{JSON}"
        try:
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            with Path.open(stats_path, "w") as f:
                f.write(stats.model_dump_json(indent=4))
        except OSError as e:
            msg = f"Failed to store {stats.sort} into {self._out_dir}"
            raise OutputError(msg) from e

    def save_graph(self, graph: Figure) -> None:
        """
        Saves graph into a .png file

        STORAGE_DIR : ../output/algo/graph.png
        """

        try:
            graph_path = self._out_dir / f"{DirType.GRAPHS.value}.{PNG}"
            graph.savefig(graph_path)
            close(graph)
        except Exception as e:
            msg = f"Failed to store graph into {self._out_dir}"
            raise OutputError(msg) from e

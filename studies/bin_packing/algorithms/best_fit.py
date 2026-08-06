from datastructures.zipziptree import ZipZipTree

from .float_epsilon import fits
from .tim_sort import tim_sort

type Key = int
type Val = float
type Bin = int
type Capacity = float


class BestFitTree(ZipZipTree[Key, Val]):
    def _augment(self, node) -> None:
        pass

    def insert(self, capacity: float, bin: int) -> None:
        super().insert((capacity, bin), bin)

    def remove(self, capacity: float, bin: int) -> None:
        super().remove((capacity, bin))


def _find_bin(tree: BestFitTree, size: float) -> ZipZipTree.Node | None:
    cur = tree._root
    best = None
    while cur is not None:
        cap = cur.key[0]  # unpack here — find still touches raw nodes
        if fits(size, cap):
            best = cur
            cur = cur.left
        else:
            cur = cur.right
    return best


def best_fit(items: list[float], assignment: list[int], free_space: list[float]) -> None:
    """ """

    bin_capacity = 1.0
    tree = BestFitTree(capacity=max(len(items), 2))
    num_bins = 0

    for i, size in enumerate(items):
        node = _find_bin(tree, size)
        if node is None:
            bin = num_bins
            rc: Capacity = bin_capacity - size

            tree.insert(rc, bin)
            free_space.append(rc)

            num_bins += 1
        else:
            bin = node.val
            cap = node.key[0]
            rc: Capacity = cap - size

            # AUGMENT by repeatedly removing and reinserting
            tree.remove(cap, bin)
            tree.insert(rc, bin)

            free_space[bin] = rc
            free_space[bin] = free_space[bin]

        assignment[i] = bin


def best_fit_decreasing(
    items: list[float],
    assignment: list[int],
    free_space: list[float],
    csort: callable = tim_sort,
) -> None:
    """
    Sorts the items list in descending order, then performs best fit
    """
    csort(items)
    items.reverse()
    best_fit(items, assignment, free_space)

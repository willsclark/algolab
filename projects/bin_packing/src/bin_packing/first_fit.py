from src.bin_packing.float_epsilon import fits
from src.data_structures.zipzip_tree import ZipZipTree
from src.sorts.tim_sort import tim_sort

type Key = int
type Val = float

type Bin = int

DIGITS = 2


class FirstFitTree(ZipZipTree[Key, Val]):
    """
    Augmented ZipZip Tree for FF and FFD bin packing
    """

    def _augment(self, node) -> None:
        node.brc = node.val
        if node.left is not None:
            node.brc = max(node.brc, node.left.brc)
        if node.right is not None:
            node.brc = max(node.brc, node.right.brc)


def _find_bin(tree: FirstFitTree, size: float):
    cur = tree._root
    if cur is None or not fits(size, cur.brc):
        return None
    while cur is not None:
        if cur.left is not None and fits(size, cur.left.brc):
            cur = cur.left
        elif fits(size, cur.val):
            return cur
        else:
            cur = cur.right
    return None


def first_fit(
    items: list[float], assignment: list[int], free_space: list[float]
) -> None:
    bin_capacity = 1.0
    tree = FirstFitTree(capacity=max(len(items), 2))
    num_bins = 0

    for i, size in enumerate(items):
        node = _find_bin(tree, size)
        if node is None:
            bin_key = num_bins
            new_node_size = round(bin_capacity - size, DIGITS)
            tree.insert(bin_key, new_node_size)
            free_space.append(new_node_size)
            num_bins += 1
        else:
            bin_key = node.key
            node.val -= size
            node.val = round(node.val, DIGITS)
            free_space[bin_key] -= size
            free_space[bin_key] = round(free_space[bin_key], DIGITS)
            tree._augment(node)
            tree._augment_ancestors(node)

        assignment[i] = bin_key


def first_fit_decreasing(
    items: list[float],
    assignment: list[int],
    free_space: list[int],
    csort: callable = tim_sort,
) -> None:
    """
    Sorts the list first via tim-sort/skip sort
    """
    csort(items)
    items.reverse()
    first_fit(items, assignment, free_space)

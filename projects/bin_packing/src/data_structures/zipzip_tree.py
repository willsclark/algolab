from __future__ import annotations

import random
from dataclasses import dataclass
from functools import cached_property
from math import log2

SEED = 123
RNG = random.Random(SEED)


class ZipZipTree[KeyType, ValType]:
    @dataclass
    class Node:
        """
        Defines a node in the Zip Tree.
        """

        key: KeyType
        val: ValType
        rank: ZipZipTree.Rank
        left: ZipZipTree.Node | None = None
        right: ZipZipTree.Node | None = None

    @dataclass
    class Rank:
        """
        Rank is a container representing each node's rank,
        both geometric and uniform.
        """

        geometric_rank: int
        uniform_rank: int

    type Probability = float
    type Interval = tuple[int, int]

    def __init__(self, capacity: int):
        self._capacity = capacity
        self._rng = RNG if RNG is not None else random.Random()
        self._size = 0
        self._height = 0
        self._root: ZipZipTree.Node | None = None

    @property
    def get_capacity(self) -> int:
        return self._capacity

    @cached_property
    def unif_range(self) -> Interval:
        """Returns the range for the uniform dist.
        over [0, 1, ..., log_2 (capacity)^3 - 1]

        """
        end = int(log2(self._capacity) ** 3) - 1
        return (0, end) if end >= 1 else (0, 1)

    def insert(self, key: KeyType, val: ValType, rank: Rank = None):
        """
        Inserts a node x into the Zip tree.

        :Params:
            key: KeyType; the key of the node, x to insert
            val: ValType; x.value
            rank: Rank  ; the rank of the node (dist via geom/unif)

        :Returns:
            success: Boolean; if the insert was successful
        """

        if rank is None:
            rank = self.get_random_rank()

        X = ZipZipTree.Node(key, val, rank)

        cur: ZipZipTree.Node = self._root

        while cur is not None and (
            rank < cur.rank or (rank == cur.rank and key > cur.key)
        ):
            prev = cur
            if key < cur.key:
                cur = cur.left
            else:
                cur.right

        if cur == self._root:
            self._root = X
        elif key < prev.key:
            prev.left = X
        else:
            prev.right = X

        if cur is None:
            return

        if key < cur.key:
            X.right = cur
        else:
            X.left = cur
        prev = X

        while cur is not None:
            fix = prev
            if cur.key < key:
                while cur is not None and cur.key > key:
                    prev = cur
                    cur = cur.right
            else:
                while cur is not None and cur.key < key:
                    prev = cur
                    cur = cur.left

            if fix.key > key or (fix == X and prev.key > key):
                fix.left = cur
            else:
                fix.right = cur

    def find(self, key: KeyType) -> ValType:
        """Searches the zip-zip tree for the item with key

        :Params:
            key (KeyType): the key of the node

        :Returns:
            value: the value of the node with key "key"
        """
        return self._find_node(key).val

    def remove(self, key: KeyType) -> bool:
        """
        Removes a node X from the tree

        :Returns: boolean if removal was successful
        """

        X = self._find_node(key)

        cur = self._root
        while key != cur.key:
            prev = cur
            if key < cur.key:
                cur = cur.left
            else:
                cur = cur.right
        left = cur.left
        right = cur.right

        if left is None:
            cur = right
        elif right is None:
            cur = left
        elif left.rank >= right.rank:
            cur = left
        else:
            cur = right

        if self._root == X:
            self._root = cur
        elif key < prev.key:
            prev.left = cur
        else:
            prev.right = cur

        while left is not None and right is not None:
            if left.rank >= right.rank:
                while left is not None and left.rank >= right.rank:
                    prev = left
                    left = left.right
                prev.right = right
            else:
                while left is not None and left.rank < right.rank:
                    prev = right
                    right = right.left
                    prev.left = left

    def get_random_rank(self) -> ZipZipTree.Rank:
        """
        :returns: a random node rank, chosen independently from:
            - a geometric distribution with E[geom] = 1
            - a uniform distribution over [0, log(capacity)^3 - 1]
        """
        geom = 0
        while self._bernouli(0.5):
            geom += 1

        unif = self._rng.randint(*self.unif_range)

        return ZipZipTree.Rank(geom, unif)

    def get_size(self) -> int:
        """
        :Returns: the number of nodes in the tree
        """
        return self._size

    def get_height(self) -> int:
        """
        Returns:
            height: the distance from root -> leaf
        """
        return self._root.rank.geometric_rank if self._root else 0

    def get_depth(self, key: KeyType) -> int:
        """
        :Returns:
            depth: (int); the distance from key -> root.

        """
        x = self._find_node(key)
        return self._height - x.rank.geometric_rank

    def _bernouli(self, p: Probability) -> int:
        """
        calculates a random geometric R.V. trial with
        X follows geom(p)
        """
        return 1 if self._rng.random() < p else 0

    def _find_node(self, key: KeyType) -> Node:
        """
        Finds a node from a key
        (Assumes the node exists)
        """
        ...

    def __len__(self) -> int:
        return self._size

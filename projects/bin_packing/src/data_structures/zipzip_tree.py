# insert(): inserts item with parameter key, value, and rank into tree.
#           if rank is not provided, a random rank should be selected by using get_random_rank().
# remove(): removes item with parameter key from tree.
#           you can assume that the item exists in the tree.
# find(): returns the value of item with parameter key.
#         you can assume that the item exists in the tree.
# get_size(): returns the number of nodes in the tree.
# get_height(): returns the height of the tree.
# get_depth(): returns the depth of the item with parameter key.
#              you can assume that the item exists in the tree.

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Rank:
    """
    Rank is a container representing each node's rank,
    both geometric and uniform.
    """

    geometric_rank: int
    uniform_rank: int


class ZipZipTree[KeyType, ValType]:
    def __init__(self, capacity: int):
        """constructs the zip-zip tree with a specific capacity"""
        self._capacity = capacity

    @property
    def get_capacity(self) -> int:
        return self._capacity

    def get_random_rank(self) -> Rank:
        """
        :returns: a random node rank, chosen independently from:
            - a geometric distribution with E[geom] = 1
            - a uniform distribution over [0, log(capacity)^3 - 1]
        """
        pass

    def insert(self, key: KeyType, val: ValType, rank: Rank = None) -> bool:
        """
        Inserts a node x into the Zip tree.

        :Params:
            key: KeyType; the key of the node, x to insert
            val: ValType; x.value
            rank: Rank  ; the rank of the node (dist via geom/unif)

        :Returns:
            success: Boolean; if the insert was successful
        """
        pass

    def remove(self, key: KeyType) -> bool:
        """
        Removes a node X from the tree

        :Returns: boolean if removal was successful
        """
        pass

    def search(self, key: KeyType) -> ValType:
        """Searches the zip-zip tree for the item with key

        :Params:
            key (KeyType): the key of the node

        :Returns:
            value: the value of the node with key "key"
        """

    def get_size(self) -> int:
        """
        :Returns: the number of nodes in the tree
        """
        pass

    def get_height(self) -> int:
        """
        Returns:
            height: the distance from root -> leaf
        """
        pass

    def get_depth(self, key: KeyType) -> int:
        """
        :Returns:
            depth: (int); the distance from key -> root.
        """
        pass

    # feel free to define new methods in addition to the above
    # fill in the definitions of each required member function (above),
    # and for any additional member functions you define

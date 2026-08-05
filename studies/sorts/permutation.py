import math
import random


class Permutation:

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def unif(self, n: int) -> list:
        """
        Implements FisherYates
        """
        arr = list(range(1, n + 1))
        for i in range(n - 1, 0, -1):
            j = self._rng.randint(0, i)
            arr[i], arr[j] = arr[j], arr[i]
        return arr

    def almost_sorted(self, n: int) -> list:
        arr = list(range(1, n + 1))
        num_swaps = max(1, int(math.log2(n)))

        for _ in range(num_swaps):
            i = self._rng.randint(0, n - 1)
            j = self._rng.randint(0, n - 1)
            arr[i], arr[j] = arr[j], arr[i]

        return arr

    def two_alternating(self, n: int) -> list:
        if n % 2 != 0:
            raise ValueError("n must be even")

        return list(range(1, n + 1, 2)) + list(range(2, n + 1, 2))

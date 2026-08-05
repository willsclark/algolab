"""Psuedocode:

Input: A sequence S to sort
Result: A modified sequence S


gap <- a.length / 2;
for (gap = S.length / 2, gap > 0, gap /= 2)
    for (int i = gap; i < S.length; i++)
        // slide element i back by gap indexes
        // until its "in order"
        int temp = a[i];
        int j = i;
        while (j >= gap && temp < a[j - gap]){
            a[j] = a[j - gap];
            j -= gap;
        }
        a[j] = temp;

"""

from sorts.tim_sort import tim_sort


def shell_sort(S: list, gaps: list) -> tuple:
    comparisons = 0
    for gap in gaps:
        for i in range(gap, len(S)):
            temp = S[i]

            j = i
            while j >= gap:
                comparisons += 1
                if temp < S[j - gap]:
                    S[j] = S[j - gap]
                    j -= gap
                else:
                    break
            S[j] = temp
    return (comparisons, S)


def _gaps_shell(S) -> list:
    """Implements the original shell function, [n/2^k], where
    [*] denotes the floor function, k <- 1, 2, ... logn
    """
    gaps = []
    g = len(S) // 2
    while g > 0:
        gaps.append(g)

        g = g // 2
    return gaps


def _gaps_shell2(S) -> list:
    """Implements the sequence 2[n/2^(k + 1)] + 1, where
    [*] denotes the floor function, k <- 1, 2, ... log n
    """
    gaps = []
    n = len(S)
    k = 0
    g = 2 * (n // (2 ** (k + 1))) + 1
    while g > 1:
        gaps.append(g)
        k += 1
        g = 2 * (n // (2 ** (k + 1))) + 1
    # function hangs if we allow gap size of 1 in the loop <- add later
    gaps.append(1)
    return gaps


def _gaps_A083318(S) -> list:
    """Implements A083318, 2^k + 1.
    k <- log n, ..., 2, 1
    """

    gaps = []
    n = len(S)
    k = 0
    g = 1  # a(0) = 1 per the docs

    while g < n:
        gaps.append(g)
        k += 1
        g = 2**k + 1

    return gaps[::-1]


def _gaps_A003586(S) -> list:
    """Implements A003586 2^p3^q
    '3-smooth numbers' where p, q >= 0, and
    p,q <- max(p, q) < n ... 1
    """
    gaps = []

    n = len(S)
    p = 0

    while 2**p < n:
        q = 0

        while 2**p * 3**q < n:
            gaps.append(2**p * 3**q)
            q += 1
        p += 1

    tim_sort(gaps)
    gaps.reverse()
    return gaps


def _gaps_A003462(S) -> list:
    """A003462, where a(n) = (3^n - 1)/2 for
    max_k < n -> 1
    """

    gaps = []
    n = len(S)
    k = 1
    g = 1  # (3 - 1) / 2 = 1, can't have 0 gaps

    while g < n:
        gaps.append(g)
        k += 1
        g = (3**k - 1) // 2
    return gaps[::-1]


def shell_sort1(S) -> tuple:
    return shell_sort(S, _gaps_shell(S))


def shell_sort2(S) -> tuple:
    return shell_sort(S, _gaps_shell2(S))


def shell_sort3(S) -> tuple:
    return shell_sort(S, _gaps_A083318(S))


def shell_sort4(S) -> tuple:
    return shell_sort(S, _gaps_A003586(S))


def shell_sort5(S) -> tuple:
    return shell_sort(S, _gaps_A003462(S))

"""tim_sort.py

ALGORITHM PSUEDOCODE:
Input: A sequence S to sort
Result: The sequence S is sorted into a single run, which remains on the stack
Note: At any time, we denote the height of the stack R by h and its i'th top-most
run (for i <= i <= h) by R_i. The size of this run is denoted by r_i.

runs <- the run decomposition of S
R <- an empty stack
while runs != 0 do
    remove a run r from runs and push r onto R
    while true do
        if h >= 3 and r_1 > r_3 then merge the runs R_2 and R_3
        else if h >= 2 and r_1 >= r_2 then merge the runs R_1 and R_2
        else if h >= 3 and r_1 + r_2 >= r_3 then merge the runs R_1 and R_2
        else if h >= 4 and r_2 + r_3 >= r_4 then merge the runs R_1 and R_2
        else break

while H != 1 do merge the runs R_1 and R_2
"""

from typing import NamedTuple


class Run(NamedTuple):
    start_idx: int
    length: int


def tim_sort(S: list) -> tuple:
    comparisons = 0

    if len(S) <= 1:  # nothing to merge; a 0- or 1-element list is already sorted
        return (comparisons, S)

    runs = _get_run_decomposition(S)
    R: list[Run] = []  # empty stack

    while runs:

        r = runs.pop()
        R.append(r)

        while True:
            h = len(R)  # height of the stack
            if h >= 3 and R[-1].length > R[-3].length:
                comparisons += merge_runs(S, R, -3, -2)
            elif h >= 2 and R[-1].length >= R[-2].length:
                comparisons += merge_runs(S, R, -2, -1)
            elif h >= 3 and R[-1].length + R[-2].length >= R[-3].length:
                comparisons += merge_runs(S, R, -2, -1)
            elif h >= 4 and R[-2].length + R[-3].length >= R[-4].length:
                comparisons += merge_runs(S, R, -2, -1)
            else:
                break
    while len(R) != 1:
        comparisons += merge_runs(S, R, -2, -1)
    return (comparisons, S)


def _get_run_decomposition(S: list) -> list[Run]:
    """


    Params: S, a sequence

    Returns: list[Run]
        - A list of Run objects

    """

    decomp: list[Run] = []
    i = 0
    n = len(S)

    while i < n:
        start = i

        # BASE CASE
        if i == n - 1:
            decomp.append(Run(start, 1))
            break

        i += 1
        ascending: bool = S[i] >= S[i - 1]

        if ascending:  # ascending can be non-decreasing
            while i < n and S[i] >= S[i - 1]:
                i += 1
        else:  # descending MUST be strictly decreasing
            while i < n and S[i] < S[i - 1]:
                i += 1
            # reverse order
            S[start:i] = S[start:i][::-1]
        decomp.append(Run(start, i - start))

    # reverse decomp to be "stacky"
    return decomp[::-1]


def merge_runs(S: list, R: list[Run], i: int, j: int) -> int:
    """
    Handles the main run-merging logic for tim-sort

    Params: S, the original sequence to be sorted
            R, the current stack of runs
            indices i, j of the merged runs into R (to avoid copying Ri, Rj)
    """
    min_r_idx = min(i, j)
    max_r_idx = max(i, j)
    r_i: Run = R[i]
    r_j: Run = R[j]

    merge_idx = min(r_i.start_idx, r_j.start_idx)
    merged_length = r_i.length + r_j.length

    comparisons = _merge_subarray(S, merge_idx, r_i.length, r_j.length)

    # modify R
    R[min_r_idx] = Run(merge_idx, merged_length)
    del R[max_r_idx]

    return comparisons


def _merge_subarray(S: list, merge_idx: int, len_s1: int, len_s2: int) -> int:
    """

    S[merge_idx : merge_idx + len_s1]  — first sorted run
    S[merge_idx + len_s1 : merge_idx + len_s1 + len_s2] — second sorted run
    """

    comparisons = 0
    left = S[merge_idx : merge_idx + len_s1]
    right = S[merge_idx + len_s1 : merge_idx + len_s1 + len_s2]

    i = 0  # pointer into left
    j = 0  # pointer into right
    k = merge_idx  # write pointer into S

    while i < len_s1 and j < len_s2:
        comparisons += 1
        if left[i] <= right[j]:
            S[k] = left[i]
            i += 1
        else:
            S[k] = right[j]
            j += 1
        k += 1

    while i < len_s1:
        S[k] = left[i]
        i += 1
        k += 1

    while j < len_s2:
        S[k] = right[j]
        j += 1
        k += 1

    return comparisons

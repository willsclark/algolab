# Example file: next_fit.py
from src.bin_packing.float_epsilon import fits


def next_fit(items: list[float], assignment: list[int], free_space: list[float]):
    """
    :params:
            items: the items to assign to the bins
            assignment: the assignment of the ith item to the jth bin for all i items.
                            bin numbers start from 0.
                            assume len(assignment) == len(items).
                            you should not add any new elements to this list.
                            you must modify this list's elements to indicate the assignment.
                            see comment below for first-fit decreasing and for best-fit decreasing.

            free_space: the amount of space left in the jth bin for all j bins created by the algorithm.
                                    you should add one element for each bin that the algorithm creates.
                                    when the function returns, this should indicate the final free space available in each bin.
    """
    NDIGITS = 2
    bin_capacity = 1.0
    cur_bin = 0
    free_space.append(bin_capacity)
    for i in range(len(items)):
        if not fits(items[i], free_space[cur_bin]):
            cur_bin += 1
            free_space.append(1.0)

        # put item in current bin
        assignment[i] = cur_bin
        # decrement space
        free_space[cur_bin] -= items[i]
        free_space[cur_bin] = round(free_space[cur_bin], NDIGITS)

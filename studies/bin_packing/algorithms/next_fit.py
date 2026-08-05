from .float_epsilon import fits


def next_fit(items: list[float], assignment: list[int], free_space: list[float]):
    """Pack items left to right, keeping only the current bin open.

    Fills ``assignment[i]`` with item i's bin (0-indexed) and appends one entry
    to ``free_space`` per bin opened, holding its final remaining capacity.
    """
    bin_capacity = 1.0
    cur_bin = 0
    free_space.append(bin_capacity)
    for i in range(len(items)):
        if not fits(items[i], free_space[cur_bin]):
            cur_bin += 1
            free_space.append(bin_capacity)

        # put item in current bin
        assignment[i] = cur_bin
        # decrement space
        free_space[cur_bin] -= items[i]

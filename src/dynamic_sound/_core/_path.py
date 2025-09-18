from typing import List, Tuple


def get_position(path: List[Tuple[float, Tuple[float, float, float]]], t: float) -> Tuple[float, float, float]:

    # Edge case: before the first time
    if t <= path[0][0]:
        return path[0][1]

    # Iterate over consecutive pairs of points
    for i in range(len(path) - 1):
        t0, p0 = path[i]
        t1, p1 = path[i + 1]

        if t0 <= t <= t1:
            # Linear interpolation factor
            alpha = (t - t0) / (t1 - t0)
            return tuple(p0[j] + alpha * (p1[j] - p0[j]) for j in range(3))

    # If t is greater than last time → return last position
    return path[-1][1]

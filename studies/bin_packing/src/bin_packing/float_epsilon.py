EPS = 10e-6


def approx_eq(a: float, b: float, eps: float = EPS) -> bool:
    return abs(a - b) <= eps


def approx_le(a: float, b: float, eps: float = EPS) -> bool:
    return a <= b + eps


def approx_lt(a: float, b: float, eps: float = EPS) -> bool:
    return a < b - eps


def fits(item: float, remaining: float, eps: float = EPS) -> bool:
    return approx_le(item, remaining, eps)


def is_full(remaining: float, eps: float = EPS) -> bool:
    return approx_le(remaining, 0.0, eps)

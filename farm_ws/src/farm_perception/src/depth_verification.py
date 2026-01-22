"""Depth verification for sampling (stub)."""


def verify_depth(depth_mm: float, min_mm: float = 10.0, max_mm: float = 200.0) -> bool:
    """Return True if depth within valid range."""
    return min_mm <= depth_mm <= max_mm

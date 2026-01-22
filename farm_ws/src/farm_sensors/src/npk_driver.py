#!/usr/bin/env python3
"""NPK sensor driver (stub). Returns simulated N, P, K values."""

import random


def read_npk():
    """Return (nitrogen, phosphorus, potassium) in mg/kg."""
    return (
        random.uniform(10.0, 50.0),
        random.uniform(5.0, 30.0),
        random.uniform(15.0, 40.0),
    )

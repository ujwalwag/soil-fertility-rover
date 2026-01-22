#!/usr/bin/env python3
"""Moisture sensor driver (stub). Returns simulated moisture percentage."""

import random


def read_moisture():
    """Return moisture percentage 0–100."""
    return random.uniform(20.0, 80.0)

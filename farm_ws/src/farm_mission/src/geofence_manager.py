#!/usr/bin/env python3
"""Geofence manager: validates points and manages boundary polygon."""

from geometry_msgs.msg import PolygonStamped, Point
import numpy as np


class GeofenceManager:
    def __init__(self):
        self.polygon: PolygonStamped | None = None

    def set_geofence(self, msg: PolygonStamped):
        self.polygon = msg

    def contains(self, x: float, y: float) -> bool:
        if self.polygon is None or len(self.polygon.polygon.points) < 3:
            return False
        pts = self.polygon.polygon.points
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)

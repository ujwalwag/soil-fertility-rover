#!/usr/bin/env python3
"""Generate farm_map.pgm from farm_world_light.world layout.
Creates an accurate top-down occupancy map matching the simulation.
"""

import os

# Map parameters - match farm_map.yaml
RESOLUTION = 0.1  # m per pixel
WORLD_SIZE = 100.0  # meters
ORIGIN_X = -50.0
ORIGIN_Y = -50.0
PIXELS = int(WORLD_SIZE / RESOLUTION)  # 1000 x 1000

# Occupancy values
FREE = 254
UNKNOWN = 205
OCCUPIED = 0

# Spawn area (for reference)
SPAWN = (9.0, 9.0)

# Maize row layout from farm_world_light.world
# Rows: y from -7.12 to 1.28, step 1.2 (8 rows)
# Plants: x from -7.92 to 7.28, step 0.8 (20 per row)
MAIZE_ROWS = [
    -7.12, -5.92, -4.72, -3.52, -2.32, -1.12, 0.08, 1.28
]
MAIZE_X = [-7.92 + i * 0.8 for i in range(20)]
MAIZE_RADIUS = 0.15  # footprint radius in m

# Fence posts
FENCE_POSTS = [(10, 10), (-10, 10)]
FENCE_SIZE = 0.15  # half-size for 0.1x0.1 box

# Trees: (x, y, foliage_radius)
TREES = [
    (15, 15, 2.0), (-15, 15, 2.0), (15, -15, 2.0), (-15, -15, 2.0),
    (20, 0, 2.0), (-20, 0, 2.0),
]


def world_to_pixel(x: float, y: float) -> tuple[int, int]:
    """Convert world (x,y) to image (col, row). Origin at bottom-left."""
    col = int((x - ORIGIN_X) / RESOLUTION)
    row = PIXELS - 1 - int((y - ORIGIN_Y) / RESOLUTION)  # flip Y for image
    return (col, row)


def draw_circle(img, cx: int, cy: int, r_px: int, value: int):
    """Fill circle in image."""
    for dy in range(-r_px, r_px + 1):
        for dx in range(-r_px, r_px + 1):
            if dx * dx + dy * dy <= r_px * r_px:
                px, py = cx + dx, cy + dy
                if 0 <= px < PIXELS and 0 <= py < PIXELS:
                    img[py][px] = value


def draw_square(img, cx: int, cy: int, half: int, value: int):
    """Fill square in image."""
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < PIXELS and 0 <= py < PIXELS:
                img[py][px] = value


def draw_grid_lines(img, interval_m: float = 10.0):
    """Draw grid lines every interval_m meters."""
    step_px = int(interval_m / RESOLUTION)
    grid_val = 220  # Slightly darker than free
    for i in range(0, PIXELS + 1, step_px):
        for row in range(PIXELS):
            img[row][min(i, PIXELS - 1)] = grid_val
        for col in range(PIXELS):
            img[min(i, PIXELS - 1)][col] = grid_val


def main():
    # Initialize: free space, clean field
    img = [[FREE] * PIXELS for _ in range(PIXELS)]

    # Grid lines every 10m
    draw_grid_lines(img, 10.0)

    # Maize rows: light strip (no dots), just row boundaries
    for y in MAIZE_ROWS:
        cy = world_to_pixel(0, y)[1]
        for col in range(PIXELS):
            if 0 <= cy < PIXELS:
                img[cy][col] = 230
            if 0 <= cy + 1 < PIXELS:
                img[cy + 1][col] = 230

    # No fence/tree dots - grid + maize rows only (clean map)

    # Write PGM
    script_dir = os.path.dirname(os.path.abspath(__file__))
    map_dir = os.path.join(script_dir, "..", "config", "maps")
    os.makedirs(map_dir, exist_ok=True)
    pgm_path = os.path.join(map_dir, "farm_map.pgm")

    with open(pgm_path, "w") as f:
        f.write("P2\n")
        f.write(f"# Farm map - matches farm_world_light.world top-down\n")
        f.write(f"{PIXELS} {PIXELS}\n")
        f.write("255\n")
        for row in img:
            f.write(" ".join(str(p) for p in row) + "\n")

    print(f"Generated {pgm_path} ({PIXELS}x{PIXELS}, resolution {RESOLUTION} m/px)")
    print(f"Origin: [{ORIGIN_X}, {ORIGIN_Y}]")


if __name__ == "__main__":
    main()

import numpy as np
from config import WIDTH, HEIGHT

def find_max_min_value(heightmap):
    max_value = np.max(heightmap)
    min_value = np.min(heightmap)
    print(f"Max value: {max_value}, Min value: {min_value}")

def correct_position(x, y):
    # Avoid it goes out of bounds
    if x > WIDTH:
        x = WIDTH - 1
    if y > HEIGHT:
        y = HEIGHT - 1
    return x, y
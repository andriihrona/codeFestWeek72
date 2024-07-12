import numpy as np

def generate_colored_heightmap(heightmap):
    height, width = heightmap.shape
    colored_map = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            height_value = heightmap[i, j]
            if height_value == 0:
                colored_map[i, j] = [0, 105, 148]  # Blue for water
            elif height_value == 1:
                colored_map[i, j] = [208, 187, 148]  # Brown for ground
            else:
                colored_map[i, j] = [120, 14, 0]  # Red for mountain
    return colored_map

def create_heightmap_with_circle(size, radius):
    heightmap = np.full((size, size), 0, dtype=np.uint8)
    center = size // 2
    for i in range(size):
        for j in range(size):
            distance = np.sqrt((i - center) ** 2 + (j - center) ** 2)
            if distance < radius*0.9:
                heightmap[i, j] = 2
            elif distance < radius * 1.4:
                heightmap[i, j] = 1
    return heightmap

def create_heightmap_with_middle_band(size, radius):
    heightmap = np.full((size, size), 1, dtype=np.uint8)
    center = size // 2
    band_width = size // 10  # Calculate the band width as 1/10 of the size
    band_start = center - band_width // 2
    band_end = center + band_width // 2

    for i in range(size):
        for j in range(size):
            distance = np.sqrt((i - center) ** 2 + (j - center) ** 2)
            if band_start <= j < band_end:  # Create the mountain band in the middle
                heightmap[i, j] = 2
            elif distance < radius * 0.9:
                heightmap[i, j] = 2
            elif distance < radius * 1.4:
                heightmap[i, j] = 1

    return heightmap
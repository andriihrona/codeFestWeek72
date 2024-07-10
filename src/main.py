import pygame
import numpy as np
import math
from species import Rabbit, AdvantagedRabbit, Fox
import random
from out import get_depth, find_projector_screen, show_image_on_projector
import cv2

def check_collision(species1, species2):
    distance = math.sqrt((species1.position[0] - species2.position[0]) ** 2 +
                         (species1.position[1] - species2.position[1]) ** 2)
    return distance < (species1.radius + species2.radius)

def generate_colored_heightmap(heightmap):
    height, width = heightmap.shape
    colored_map = np.zeros((height, width, 3), dtype=np.uint8)
    third_height = 255 // 3
    for i in range(height):
        for j in range(width):
            height_value = heightmap[i, j]
            if height_value < third_height:
                colored_map[i, j] = [0, 0, 255]  # Blue for lowest third
            elif height_value < 2 * third_height:
                colored_map[i, j] = [139, 69, 19]  # Brown for middle third
            else:
                colored_map[i, j] = [255, 1, 1]  # Red for highest third
    return colored_map

def normalize_heightmap(depth_map):
    # Assuming depth_map is in RGB format, convert to grayscale
    depth_map_gray = cv2.cvtColor(depth_map, cv2.COLOR_RGB2GRAY)
    min_depth = np.min(depth_map_gray)
    max_depth = np.max(depth_map_gray)
    heightmap = ((depth_map_gray - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)
    return heightmap

pygame.init()

# Find the projector screen size if available
projector = find_projector_screen()
window_size = (projector.width, projector.height)

# Initialize heightmap with the first frame of depth data
depth = get_depth()
heightmap = normalize_heightmap(depth)

colored_heightmap = generate_colored_heightmap(heightmap)
colored_surface = pygame.surfarray.make_surface(colored_heightmap)

rabbits = [Rabbit((300 + i * 20, 300)) for i in range(3)]
advantaged_rabbits = [AdvantagedRabbit((300 + i * 20, 350)) for i in range(2)]
foxes = [Fox((250 + i * 10, 200)) for i in range(2)]

screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Ecosystem Simulation")


# # Move window to the projector screen coordinates

# pygame.display.set_mode(window_size, pygame.NOFRAME)
# pygame.display.set_mode(window_size, pygame.FULLSCREEN)
# pygame.display.set_mode((projector.width, projector.height), pygame.NOFRAME)
# pygame.display.set_mode((projector.width, projector.height), pygame.FULLSCREEN)



clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    rabbits = [rabbit for rabbit in rabbits if not rabbit.age()]
    advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not advantaged_rabbit.age()]
    foxes = [fox for fox in foxes if not fox.age()]

    for fox in foxes:
        fox.pursue(rabbits + advantaged_rabbits, heightmap)

    for rabbit in rabbits:
        rabbit.flee(foxes, heightmap)
    for advantaged_rabbit in advantaged_rabbits:
        advantaged_rabbit.flee(foxes, heightmap)

    def breed_species(species_list):
        new_offsprings = []
        num_to_breed = len(species_list) // 2
        breeders = random.sample(species_list, num_to_breed)
        for species in breeders:
            if species.can_breed():
                new_offsprings.extend([species.breed() for _ in range(species.breeding_coefficient)])
        species_list.extend(new_offsprings)

    breed_species(rabbits)
    breed_species(advantaged_rabbits)
    breed_species(foxes)

    rabbits = [rabbit for rabbit in rabbits if not any(check_collision(rabbit, fox) for fox in foxes)]
    advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not any(check_collision(advantaged_rabbit, fox) for fox in foxes)]

    # Update heightmap with the latest depth data
    depth = get_depth()
    heightmap = normalize_heightmap(depth)
    colored_heightmap = generate_colored_heightmap(heightmap)
    colored_surface = pygame.surfarray.make_surface(colored_heightmap)

    screen.fill((0, 0, 0))
    screen.blit(colored_surface, (0, 0))

    for rabbit in rabbits:
        pygame.draw.circle(screen, rabbit.color, rabbit.position, rabbit.radius)
    for advantaged_rabbit in advantaged_rabbits:
        pygame.draw.circle(screen, advantaged_rabbit.color, advantaged_rabbit.position, advantaged_rabbit.radius)
    for fox in foxes:
        pygame.draw.circle(screen, fox.color, fox.position, fox.radius)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()

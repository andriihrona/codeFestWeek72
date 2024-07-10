import pygame
import numpy as np
import math
from species import Rabbit, AdvantagedRabbit, Fox
import random

def check_collision(species1, species2):
    distance = math.sqrt((species1.position[0] - species2.position[0]) ** 2 +
                         (species1.position[1] - species2.position[1]) ** 2)
    return distance < (species1.radius + species2.radius)

def generate_colored_heightmap(heightmap):
    height, width = heightmap.shape
    colored_map = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            height_value = heightmap[i, j]
            if height_value == 0:
                colored_map[i, j] = [0, 0, 255]  # Blue for water
            elif height_value == 11:
                colored_map[i, j] = [139, 69, 19]  # Brown
            else:
                colored_map[i, j] = [255, 0, 0]  # Red
    return colored_map

def create_heightmap_with_circle(size, radius):
    heightmap = np.full((size, size), 21, dtype=np.uint8)
    center = size // 2
    for i in range(size):
        for j in range(size):
            distance = np.sqrt((i - center) ** 2 + (j - center) ** 2)
            if distance < radius:
                heightmap[i, j] = 0
            elif distance < radius * 1.5:
                heightmap[i, j] = 11
    return heightmap

pygame.init()

size = 640
radius = size // 4
heightmap = create_heightmap_with_circle(size, radius)
colored_heightmap = generate_colored_heightmap(heightmap)
colored_surface = pygame.surfarray.make_surface(colored_heightmap)

rabbits = [Rabbit((300 + i * 20, 300)) for i in range(4)]
advantaged_rabbits = [AdvantagedRabbit((300 + i * 20, 350)) for i in range(4)]
foxes = [Fox((250+i*10, 200)) for i in range(2)]

window_size = (size, size)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Ecosystem Simulation")

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

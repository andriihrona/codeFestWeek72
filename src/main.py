import pygame
import numpy as np
import math
from species import Rabbit, AdvantagedRabbit, Fox
import random
from out import get_depth, find_projector_screen, show_image_on_projector
import cv2
import freenect
import frame_convert

def check_collision(species1, species2):
    distance = math.sqrt((species1.position[0] - species2.position[0]) ** 2 +
                         (species1.position[1] - species2.position[1]) ** 2)
    return distance < (species1.radius + species2.radius)

def apply_custom_colormap(depth, min_depth=400, max_depth=550):
    depth = np.clip(depth.astype(np.float32), min_depth, max_depth)
    depth = ((depth - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)
    colormap = np.zeros((256, 1, 3), dtype=np.uint8)
    for i in range(256):
        if i < 128:
            colormap[i, 0, 0] = 255 - 2 * i  # Red decreases
            colormap[i, 0, 1] = 2 * i        # Green increases
            colormap[i, 0, 2] = 255          # Blue stays at max
        else:
            colormap[i, 0, 0] = 255          # Red stays at max
            colormap[i, 0, 1] = 255 - 2 * (i - 128)  # Green decreases
            colormap[i, 0, 2] = 2 * (i - 128)        # Blue increases
    
    depth_colormap = cv2.applyColorMap(depth, colormap)
    return depth_colormap

def apply_colormap(depth, min_depth, max_depth, mean):
    depth = np.clip(depth.astype(np.uint8), min_depth, max_depth)
    depth = ((depth - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)

    blue_threshold = int(mean + min_depth / 3)
    green_threshold = int(mean + max_depth / 2)

    colormap = np.zeros((256, 1, 3), dtype=np.uint8)
    colormap[:blue_threshold, 0, 2] = 255 #Bleu
    colormap[blue_threshold:green_threshold, 0, 1] = 255 #Vert
    colormap[green_threshold:, 0, 0] = 255 #Rouge

    depth_colormap = cv2.applyColorMap(depth, colormap)
    return depth_colormap 

def video_cv(video):
    return video[:, :, ::-1]  # RGB -> BGR

def normalize_heightmap(depth_map):
    if len(depth_map.shape) == 3 and depth_map.shape[2] == 3:
        depth_map_gray = cv2.cvtColor(depth_map, cv2.COLOR_RGB2GRAY)
    else:
        depth_map_gray = depth_map
    min_depth = np.min(depth_map_gray)
    max_depth = np.max(depth_map_gray)
    heightmap = ((depth_map_gray - min_depth) / (max_depth - min_depth) * 255).astype(np.uint8)
    return heightmap

if __name__ == "__main__":
    pygame.init()

    projector = find_projector_screen()
    window_size = (projector.width, projector.height)

    depth = get_depth()
    heightmap = normalize_heightmap(depth)

    colored_heightmap = apply_custom_colormap(depth)
    colored_surface = pygame.surfarray.make_surface(colored_heightmap)

    rabbits = [Rabbit((300 + i * 20, 300)) for i in range(3)]
    advantaged_rabbits = [AdvantagedRabbit((300 + i * 20, 350)) for i in range(2)]
    foxes = [Fox((250 + i * 10, 200)) for i in range(2)]

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Ecosystem Simulation")

    clock = pygame.time.Clock()
    running = True

    while True:
        depth = get_depth()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        rabbits = [rabbit for rabbit in rabbits if not rabbit.age()]
        advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not advantaged_rabbit.age()]
        foxes = [fox for fox in foxes if not fox.age()]

        # heightmap = depth
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
        breed_species(foxes)
        breed_species(advantaged_rabbits)

        rabbits = [rabbit for rabbit in rabbits if not any(check_collision(rabbit, fox) for fox in foxes)]
        advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not any(check_collision(advantaged_rabbit, fox) for fox in foxes)]

        depth = get_depth()
        heightmap = normalize_heightmap(depth)
        colored_heightmap = apply_custom_colormap(heightmap)
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

        frame = pygame.surfarray.array3d(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        show_image_on_projector(frame, projector)

    pygame.quit()

import pygame
import random
import math
from utils.out import get_depth, find_projector_screen, show_image_on_projector, apply_colormap, normalise_depth
import os
import cv2
from species.Species import *
from species.Rabbit import *
from species.AdvantagedRabbit import *
from species.Fox import *
from config import MAX_RABBITS, MAX_ADVANTAGED_RABBITS, MAX_FOXES, SIZE

def check_collision(species1, species2):
    distance = math.sqrt((species1.position[0] - species2.position[0]) ** 2 +
                         (species1.position[1] - species2.position[1]) ** 2)
    return distance < (species1.radius + species2.radius)

if __name__ == "__main__":
    projector = find_projector_screen()

    pygame.init()

    rabbits = [Rabbit((500 + i * 20, 400)) for i in range(10)] #10
    advantaged_rabbits = [AdvantagedRabbit((400 + i * 20, 500)) for i in range(8)] #8
    foxes = [Fox((250-i*50, 300)) for i in range(2)]
    
    window_size = (SIZE, SIZE)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Ecosystem Simulation")

    while 1:
        depth = get_depth()
        colored_heightmap = apply_colormap(depth)
        colored_surface = pygame.surfarray.make_surface(colored_heightmap)

        clock = pygame.time.Clock()

        heightmap = normalise_depth(depth)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        rabbits = [rabbit for rabbit in rabbits if not rabbit.age()]
        advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not advantaged_rabbit.age()]
        foxes = [fox for fox in foxes if not fox.age()]

        for fox in foxes:
            fox.pursue(rabbits, heightmap)
            fox.pursue(advantaged_rabbits, heightmap)

        for rabbit in rabbits:
            rabbit.flee(foxes, heightmap)
        for advantaged_rabbit in advantaged_rabbits:
            advantaged_rabbit.flee(foxes, heightmap)
        for fox in foxes:
            fox.pursue(rabbits + advantaged_rabbits, heightmap)

        rabbit_icon = pygame.image.load(os.path.join(os.getcwd(), "images", "whiterabbit.png"))
        rabbit_icon = pygame.transform.scale(rabbit_icon, (20, 20))

        advantaged_rabbit_icon = pygame.image.load(os.path.join(os.getcwd(), "images", "blackrabbit.png"))
        advantaged_rabbit_icon = pygame.transform.scale(advantaged_rabbit_icon, (20, 20))

        fox_icon = pygame.image.load(os.path.join(os.getcwd(), "images", "fox3.png"))
        fox_icon = pygame.transform.scale(fox_icon, (20, 20))

        new_rabbits = []
        new_advantaged_rabbits = []
        new_foxes = []

        def breed_species(species_list, max_population):
            new_offsprings = []
            num_to_breed = len(species_list) // 2
            breeders = random.sample(species_list, num_to_breed)
            for species in breeders:
                if species.can_breed() and len(species_list) + len(new_offsprings) < max_population:
                    new_offsprings.extend([species.breed() for _ in range(species.breeding_coefficient)])
            species_list.extend(new_offsprings)

        breed_species(rabbits, MAX_RABBITS)
        breed_species(foxes, MAX_FOXES)
        breed_species(advantaged_rabbits, MAX_ADVANTAGED_RABBITS)

        rabbits.extend(new_rabbits)
        advantaged_rabbits.extend(new_advantaged_rabbits)
        foxes.extend(new_foxes)

        rabbits = [rabbit for rabbit in rabbits if not any(check_collision(rabbit, fox) for fox in foxes)]
        advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not any(check_collision(advantaged_rabbit, fox) for fox in foxes)]

        # Add the condition to handle only foxes or only rabbits
        if len(foxes) > 0 and len(rabbits) == 0 and len(advantaged_rabbits) == 0:
            foxes = []  # All foxes die ENDGAME
        elif len(foxes) == 0 and (len(rabbits) > 0 or len(advantaged_rabbits) > 0):
            foxes.extend([Fox((random.randint(0, SIZE), random.randint(0, SIZE))) for _ in range(2)])  # Two foxes pop

        screen.fill((0, 0, 0))
        screen.blit(colored_surface, (0, 0))

        for rabbit in rabbits:
            screen.blit(rabbit_icon, (rabbit.position[0] - rabbit.radius, rabbit.position[1] - rabbit.radius))
        for advantaged_rabbit in advantaged_rabbits:
            screen.blit(advantaged_rabbit_icon, (advantaged_rabbit.position[0] - advantaged_rabbit.radius, advantaged_rabbit.position[1] - advantaged_rabbit.radius))
        for fox in foxes:
            screen.blit(fox_icon, (fox.position[0] - fox.radius, fox.position[1] - fox.radius))

        pygame.display.flip()

        frame = pygame.surfarray.array3d(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        show_image_on_projector(frame, projector)

        clock.tick(100)

    pygame.quit()
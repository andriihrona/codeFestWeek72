import pygame
import numpy as np
import random
import math
from out import get_depth, find_projector_screen, show_image_on_projector, apply_colormap

class Species:
    def __init__(self, name, allowed_heights_range, position, radius, color, life=100, speed=10, breeding_coefficient=1, breeding_interval=100, invalid_zone_time_limit=1000):
        self.name = name
        self.allowed_heights_range = allowed_heights_range
        self.position = position
        self.radius = radius
        self.color = color
        self.life = life
        self.speed = speed
        self.breeding_coefficient = breeding_coefficient
        self.breeding_interval = breeding_interval
        self.time_since_last_breed = 0
        self.invalid_zone_time_limit = invalid_zone_time_limit
        self.time_in_invalid_zone = 0

    def can_walk_on(self, height_value):
        min_height, max_height = self.allowed_heights_range
        return min_height <= height_value <= max_height

    def move_randomly(self, heightmap):
        height, width = heightmap.shape
        x, y = self.position

        directions = ['up', 'down', 'left', 'right']
        direction = random.choice(directions)

        if direction == 'up' and y > self.speed:
            new_position = (x, y - self.speed)
        elif direction == 'down' and y < height - self.speed:
            new_position = (x, y + self.speed)
        elif direction == 'left' and x > self.speed:
            new_position = (x - self.speed, y)
        elif direction == 'right' and x < width - self.speed:
            new_position = (x + self.speed, y)
        else:
            new_position = self.position

        new_x, new_y = new_position
        if self.can_walk_on(heightmap[new_y, new_x]):
            self.position = new_position
            self.time_in_invalid_zone = 0  # Reset timer when moving to a valid zone
        else:
            self.time_in_invalid_zone += 1  # Increment timer when in an invalid zone

    def age(self):
        self.life -= 1
        self.time_since_last_breed += 1
        return self.life <= 0 or self.time_in_invalid_zone >= self.invalid_zone_time_limit

    def can_breed(self):
        return self.time_since_last_breed >= self.breeding_interval

    def breed(self):
        self.time_since_last_breed = 0
        return type(self)(self.position)

class Rabbit(Species):
    def __init__(self, position, fleeing_radius=40):
        super().__init__("Rabbit", (1, 2), position, 8, (255, 255, 255), life=350, speed=10, breeding_coefficient=1, breeding_interval=150, invalid_zone_time_limit=30)
        self.fleeing_radius = fleeing_radius

    def flee(self, foxes, heightmap):
        height, width = heightmap.shape
        new_position = self.position
        for fox in foxes:
            distance = np.sqrt((self.position[0] - fox.position[0]) ** 2 + (self.position[1] - fox.position[1]) ** 2)
            if distance < self.fleeing_radius:
                # Move in the opposite direction of the fox
                fx, fy = fox.position
                rx, ry = self.position
                if rx < fx and rx > self.speed:
                    new_position = (rx - self.speed, ry)
                elif rx > fx and rx < width - self.speed:
                    new_position = (rx + self.speed, ry)
                if ry < fy and ry > self.speed:
                    new_position = (rx, ry - self.speed)
                elif ry > fy and ry < height - self.speed:
                    new_position = (rx, ry + self.speed)

                new_x, new_y = new_position
                if self.can_walk_on(heightmap[new_y, new_x]):
                    self.position = new_position
                    self.time_in_invalid_zone = 0
                else:
                    self.time_in_invalid_zone += 1
                return
        self.move_randomly(heightmap)

    def move_randomly(self, heightmap):
        height, width = heightmap.shape
        x, y = self.position

        # Adjust speed based on terrain type
        current_height_value = heightmap[y, x]
        if current_height_value == 2:  # Mountain terrain
            speed = 15
        else:
            speed = self.speed

        directions = ['up', 'down', 'left', 'right']
        direction = random.choice(directions)

        if direction == 'up' and y > speed:
            new_position = (x, y - speed)
        elif direction == 'down' and y < height - speed:
            new_position = (x, y + speed)
        elif direction == 'left' and x > speed:
            new_position = (x - speed, y)
        elif direction == 'right' and x < width - speed:
            new_position = (x + speed, y)
        else:
            new_position = self.position

        new_x, new_y = new_position
        if self.can_walk_on(heightmap[new_y, new_x]):
            self.position = new_position
            self.time_in_invalid_zone = 0  # Reset timer when moving to a valid zone
        else:
            self.time_in_invalid_zone += 1  # Increment timer when in an invalid zone


class AdvantagedRabbit(Rabbit):
    def __init__(self, position, fleeing_radius=60):
        super().__init__(position, fleeing_radius)
        self.name = "Advantaged Rabbit"
        self.color = (0, 0, 0)
        self.speed = 12
        # self.breeding_coefficient = 3
        # self.breeding_interval =10000000

class Fox(Species):
    def __init__(self, position, hunting_radius=80):
        super().__init__("Fox", (1, 2), position, 10, (255, 0, 0), life=500, speed=15, breeding_coefficient=1, breeding_interval=300, invalid_zone_time_limit=90)
        self.hunting_radius = hunting_radius

    def pursue(self, rabbits, heightmap):
        height, width = heightmap.shape
        new_position = self.position
        for rabbit in rabbits:
            distance = np.sqrt((self.position[0] - rabbit.position[0]) ** 2 + (self.position[1] - rabbit.position[1]) ** 2)
            if distance < self.hunting_radius:
                # Move towards the rabbit
                fx, fy = self.position
                rx, ry = rabbit.position
                if fx < rx and fx < width - self.speed:
                    new_position = (fx + self.speed, fy)
                elif fx > rx and fx > self.speed:
                    new_position = (fx - self.speed, fy)
                if fy < ry and fy < height - self.speed:
                    new_position = (fx, fy + self.speed)
                elif fy > ry and fy > self.speed:
                    new_position = (fx, fy - self.speed)

                new_x, new_y = new_position
                if self.can_walk_on(heightmap[new_y, new_x]):
                    self.position = new_position
                    self.time_in_invalid_zone = 0
                else:
                    self.time_in_invalid_zone += 1
                return  # Move only once to pursue the nearest rabbit
        self.move_randomly(heightmap)

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


projector = find_projector_screen()

pygame.init()

MAX_RABBITS = 50
MAX_ADVANTAGED_RABBITS = 50
MAX_FOXES = 10

size = 1000
radius = size // 3

depth = get_depth()
colored_heightmap = apply_colormap(depth)

# heightmap = create_heightmap_with_circle(size, radius)
# colored_heightmap = generate_colored_heightmap(heightmap)

colored_surface = pygame.surfarray.make_surface(colored_heightmap)

rabbits = [Rabbit((500 + i * 20, 400)) for i in range(10)]
advantaged_rabbits = [AdvantagedRabbit((400 + i * 20, 500)) for i in range(8)]
foxes = [Fox((250-i*50, 300)) for i in range(2)]

window_size = (size, size)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Ecosystem Simulation")

clock = pygame.time.Clock()
running = True
while running:
    heightmap = get_depth()
    colored_heightmap = apply_colormap(heightmap)

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

    rabbit_icon = pygame.image.load("/Users/admin/Desktop/Epita/COFE/whiterabbit.png")
    rabbit_icon = pygame.transform.scale(rabbit_icon, (20, 20))

    advantaged_rabbit_icon = pygame.image.load("/Users/admin/Desktop/Epita/COFE/blackrabbit.png")
    advantaged_rabbit_icon = pygame.transform.scale(advantaged_rabbit_icon, (20, 20))

    fox_icon = pygame.image.load("/Users/admin/Desktop/Epita/COFE/fox3.png")
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

    # breed_species(rabbits, MAX_RABBITS)
    # breed_species(foxes, MAX_FOXES)
    # breed_species(advantaged_rabbits, MAX_ADVANTAGED_RABBITS)

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

    rabbits.extend(new_rabbits)
    advantaged_rabbits.extend(new_advantaged_rabbits)
    foxes.extend(new_foxes)

    rabbits = [rabbit for rabbit in rabbits if not any(check_collision(rabbit, fox) for fox in foxes)]
    advantaged_rabbits = [advantaged_rabbit for advantaged_rabbit in advantaged_rabbits if not any(check_collision(advantaged_rabbit, fox) for fox in foxes)]

    screen.fill((0, 0, 0))
    screen.blit(colored_surface, (0, 0))

    for rabbit in rabbits:
        screen.blit(rabbit_icon, (rabbit.position[0] - rabbit.radius, rabbit.position[1] - rabbit.radius))
    for advantaged_rabbit in advantaged_rabbits:
        screen.blit(advantaged_rabbit_icon, (advantaged_rabbit.position[0] - advantaged_rabbit.radius, advantaged_rabbit.position[1] - advantaged_rabbit.radius))
    for fox in foxes:
        screen.blit(fox_icon, (fox.position[0] - fox.radius, fox.position[1] - fox.radius))

    pygame.display.flip()
    clock.tick(10)

    show_image_on_projector(colored_heightmap, projector)


pygame.quit()
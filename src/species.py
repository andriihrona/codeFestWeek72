import random
import numpy as np

class Species:
    def __init__(self, name, allowed_heights_range, position, radius, color, life=100, speed=10, breeding_coefficient=1, breeding_interval=100, invalid_zone_time_limit=10):
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
    def __init__(self, position, fleeing_radius=25):
        super().__init__("Rabbit", (0, 255), position, 8, (255, 255, 255), life=80, speed=10, breeding_coefficient=1, breeding_interval=50, invalid_zone_time_limit=10)
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

class AdvantagedRabbit(Rabbit):
    def __init__(self, position, fleeing_radius=35):
        super().__init__(position, fleeing_radius)
        self.name = "Advantaged Rabbit"
        self.color = (0, 0, 0)
        self.life = 90
        self.speed = 12
        self.breeding_coefficient = 1
        self.breeding_interval = 45

class Fox(Species):
    def __init__(self, position, hunting_radius=50):
        super().__init__("Fox", (0, 255), position, 10, (255, 0, 0), life=100, speed=15, breeding_coefficient=1, breeding_interval=60, invalid_zone_time_limit=10)
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

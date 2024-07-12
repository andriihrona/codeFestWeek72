import random
from utils.utils import correct_position

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
        new_x, new_y = correct_position(new_x, new_y)
        if self.can_walk_on(heightmap[new_x, new_y]):
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

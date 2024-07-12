import random
import numpy as np
from species.Species import Species
from utils.utils import correct_position

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
                new_x, new_y = correct_position(new_x, new_y)
                if self.can_walk_on(heightmap[new_x, new_y]):
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
        y, x = correct_position(y, x)
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
        new_x, new_y = correct_position(new_x, new_y)
        if self.can_walk_on(heightmap[new_y, new_x]):
            self.position = new_position
            self.time_in_invalid_zone = 0  # Reset timer when moving to a valid zone
        else:
            self.time_in_invalid_zone += 1  # Increment timer when in an invalid zone

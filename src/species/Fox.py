from species.Species import Species
import numpy as np
from utils.utils import correct_position

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
                new_x, new_y = correct_position(new_x, new_y)
                if self.can_walk_on(heightmap[new_x, new_y]):
                    self.position = new_position
                    self.time_in_invalid_zone = 0
                else:
                    self.time_in_invalid_zone += 1
                return  # Move only once to pursue the nearest rabbit
        self.move_randomly(heightmap)

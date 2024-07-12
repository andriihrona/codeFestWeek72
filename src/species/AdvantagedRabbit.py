from species.Rabbit import Rabbit

class AdvantagedRabbit(Rabbit):
    def __init__(self, position, fleeing_radius=60):
        super().__init__(position, fleeing_radius)
        self.name = "Advantaged Rabbit"
        self.color = (0, 0, 0)
        self.speed = 12
        # self.breeding_coefficient = 3
        # self.breeding_interval =10000000
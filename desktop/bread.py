import math
import random

BREAD_W = 30
BREAD_H = 22


class Bread:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.phase = random.random() * math.pi * 2
        self.bob = 0

    def update(self, dt):
        self.phase += 2.5 * dt
        self.bob = math.sin(self.phase) * 2

    def hit(self, px, py, pw, ph):
        if not self.alive:
            return False
        cx = self.x + BREAD_W / 2
        cy = self.y + BREAD_H / 2
        return (abs(cx - (px + pw / 2)) < (BREAD_W / 2 + pw / 2) * 0.6 and
                abs(cy - (py + ph / 2)) < (BREAD_H / 2 + ph / 2) * 0.6)


def spawn_random(wa):
    x = random.uniform(wa[0] + 20, wa[2] - 50)
    y = random.uniform(wa[1] + 50, wa[3] - 80)
    return Bread(x, y)

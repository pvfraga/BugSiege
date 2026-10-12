import random

import pygame
from pygame import Vector2


class Particle:
    """Pedacinho de efeito visual (explosao de gosma). Nao colide com nada."""

    def __init__(self, position: Vector2, color: tuple):
        self.pos = Vector2(position)
        self.velocity = Vector2(random.uniform(60, 220), 0).rotate(random.uniform(0, 360))
        self.color = color
        self.radius = random.uniform(2, 5)
        self.life = random.uniform(0.3, 0.7)

    def update(self, dt: float):
        self.pos += self.velocity * dt
        self.velocity *= 0.9
        self.life -= dt

    def draw(self, window: pygame.Surface):
        if self.life > 0:
            pygame.draw.circle(window, self.color, self.pos, max(1.0, self.radius * self.life * 2))


def burst(position: Vector2, color: tuple, amount: int) -> list[Particle]:
    return [Particle(position, color) for _ in range(amount)]

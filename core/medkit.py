import pygame

from core.const import MEDKIT_LIFETIME
from core.entity import Entity


class Medkit(Entity):
    """Kit medico que alguns insetos deixam cair. Some depois de alguns segundos."""

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.lifetime = MEDKIT_LIFETIME

    def update(self, dt: float, target) -> list:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.health = 0
        return []

    def draw(self, window: pygame.Surface):
        # pisca nos ultimos 2 segundos para avisar que vai sumir
        if self.lifetime < 2 and int(self.lifetime * 8) % 2 == 0:
            return
        super().draw(window)

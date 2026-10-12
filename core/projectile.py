from pygame import Vector2

from core.entity import Entity


class Projectile(Entity):
    """Tiro do jogador (Bullet) ou cuspe acido dos insetos (Spit)."""

    def __init__(self, name: str, position: tuple, direction: Vector2, owner: str):
        super().__init__(name, position)
        self.velocity = Vector2(direction).normalize() * self.speed
        self.owner = owner  # quem disparou: 'Player' ou o nome do inseto
        self.face(self.pos + self.velocity)
        self.sync_rect()

    def update(self, dt: float, target) -> list:
        self.pos += self.velocity * dt
        self.sync_rect()
        return []

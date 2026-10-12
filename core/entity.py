from abc import ABC, abstractmethod

import pygame
from pygame import Vector2

from core.const import ENTITY_DAMAGE, ENTITY_HEALTH, ENTITY_SPEED, HITBOX_SCALE
from core.resource import load_image


class Entity(ABC):
    """Tudo que existe na arena: jogador, insetos, projeteis, kits e particulas."""

    def __init__(self, name: str, position: tuple):
        self.name = name
        self.pos = Vector2(position)
        self.base_surf = load_image(name)  # desenho virado para a direita (angulo 0)
        self.surf = self.base_surf
        self.rect = self.surf.get_rect(center=position)
        self.angle = 0.0
        self.speed = ENTITY_SPEED[name]
        self.health = ENTITY_HEALTH[name]
        self.damage = ENTITY_DAMAGE[name]
        self.last_dmg = 'None'  # quem causou o ultimo dano (usado para pontuar)
        self.flash = 0.0  # tempo piscando branco apos levar dano

    @property
    def hitbox(self) -> pygame.Rect:
        """Retangulo de colisao: menor que a imagem, sem os cantos transparentes."""
        w, h = self.base_surf.get_size()
        size = min(w, h) * HITBOX_SCALE
        box = pygame.Rect(0, 0, size, size)
        box.center = (round(self.pos.x), round(self.pos.y))
        return box

    def face(self, target: Vector2):
        """Gira o desenho para olhar na direcao de target."""
        direction = target - self.pos
        if direction.length_squared() > 0:
            self.angle = Vector2(1, 0).angle_to(direction)
        self.surf = pygame.transform.rotate(self.base_surf, -self.angle)

    def sync_rect(self):
        self.rect = self.surf.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def take_damage(self, amount: int, source: str):
        self.health -= amount
        self.last_dmg = source
        self.flash = 0.08

    def draw(self, window: pygame.Surface):
        if self.flash > 0:
            white = self.surf.copy()
            white.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
            window.blit(white, self.rect)
        else:
            window.blit(self.surf, self.rect)

    @abstractmethod
    def update(self, dt: float, target) -> list:
        """Atualiza a entidade e devolve uma lista de novas entidades criadas (tiros etc.)."""
        pass

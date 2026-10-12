import pygame
from pygame import Vector2

from core.const import (DASH_COOLDOWN, DASH_DURATION, DASH_MULTIPLIER, ENTITY_HEALTH, PLAYER_FIRE_RATE,
                        PLAYER_INVULNERABLE_TIME, WIN_HEIGHT, WIN_WIDTH)
from core.entity import Entity
from core.projectile import Projectile
from core.resource import play_sound


class Player(Entity):

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.max_health = ENTITY_HEALTH[name]
        self.fire_timer = 0.0
        self.dash_timer = 0.0      # tempo restante da esquiva em andamento
        self.dash_cooldown = 0.0   # tempo ate poder esquivar de novo
        self.dash_dir = Vector2(1, 0)
        self.invulnerable = 0.0
        self.score = 0

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerable > 0 or self.dash_timer > 0

    def take_damage(self, amount: int, source: str):
        if self.is_invulnerable:
            return
        super().take_damage(amount, source)
        self.invulnerable = PLAYER_INVULNERABLE_TIME
        play_sound('PlayerHurt', 0.6)

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def update(self, dt: float, target) -> list:
        keys = pygame.key.get_pressed()
        self.fire_timer -= dt
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.invulnerable = max(0.0, self.invulnerable - dt)

        direction = Vector2(0, 0)
        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1
        if direction.length_squared() > 0:
            direction = direction.normalize()  # diagonal nao fica mais rapida

        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_cooldown == 0:
            self.dash_dir = direction if direction.length_squared() > 0 else Vector2(1, 0).rotate(self.angle)
            self.dash_timer = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            play_sound('Dash', 0.5)

        if self.dash_timer > 0:
            self.dash_timer -= dt
            self.pos += self.dash_dir * self.speed * DASH_MULTIPLIER * dt
        else:
            self.pos += direction * self.speed * dt

        # nao deixa sair da arena
        half_w, half_h = self.base_surf.get_width() / 2, self.base_surf.get_height() / 2
        self.pos.x = max(half_w, min(WIN_WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(WIN_HEIGHT - half_h, self.pos.y))

        self.face(Vector2(target))
        self.sync_rect()
        return self.shoot(keys)

    def shoot(self, keys) -> list:
        wants_fire = pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]
        if not wants_fire or self.fire_timer > 0:
            return []
        self.fire_timer = PLAYER_FIRE_RATE
        play_sound('Shot', 0.25)
        direction = Vector2(1, 0).rotate(self.angle)
        muzzle = self.pos + direction * 22  # sai da ponta da arma
        return [Projectile('Bullet', tuple(muzzle), direction, self.name)]

    def draw(self, window: pygame.Surface):
        # pisca enquanto esta invulneravel depois de levar dano
        if self.invulnerable > 0 and int(self.invulnerable * 20) % 2 == 0:
            return
        if self.dash_timer > 0:
            ghost = self.surf.copy()
            ghost.set_alpha(90)
            offset = -self.dash_dir * 14
            window.blit(ghost, self.rect.move(round(offset.x), round(offset.y)))
        super().draw(window)

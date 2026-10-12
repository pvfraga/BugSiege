import math
import random

from pygame import Vector2

from core.const import (QUEEN_BURST_COOLDOWN, QUEEN_BURST_SHOTS, QUEEN_SUMMON_COOLDOWN, SPITTER_FIRE_RATE,
                        SPITTER_RANGE, WIN_HEIGHT, WIN_WIDTH)
from core.entity import Entity
from core.projectile import Projectile
from core.resource import play_sound


class Enemy(Entity):
    """Base dos insetos: perseguem o jogador. Cada tipo muda o jeito de se mover/atacar."""

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.entered = False  # vira True quando o inseto entra totalmente na arena

    def chase(self, dt: float, target: Vector2, factor: float = 1.0):
        direction = target - self.pos
        if direction.length_squared() > 1:
            self.pos += direction.normalize() * self.speed * factor * dt

    def keep_inside(self):
        half = self.base_surf.get_width() / 2
        inside = half <= self.pos.x <= WIN_WIDTH - half and half <= self.pos.y <= WIN_HEIGHT - half
        if inside:
            self.entered = True
        if self.entered:  # depois de entrar, nao sai mais da arena
            self.pos.x = max(half, min(WIN_WIDTH - half, self.pos.x))
            self.pos.y = max(half, min(WIN_HEIGHT - half, self.pos.y))

    def finish_move(self, target: Vector2):
        self.keep_inside()
        self.face(target)
        self.sync_rect()

    def update(self, dt: float, target) -> list:
        self.chase(dt, target.pos)
        self.finish_move(target.pos)
        return []


class Crawler(Enemy):
    """Rapido e fraco: avanca em zigue-zague."""

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.wobble = random.uniform(0, math.tau)

    def update(self, dt: float, target) -> list:
        self.wobble += dt * 6
        goal = target.pos + Vector2(0, 40).rotate(math.degrees(self.wobble))
        self.chase(dt, goal)
        self.finish_move(target.pos)
        return []


class Brute(Enemy):
    """Lento e resistente: so anda reto ate o jogador (comportamento da classe base)."""
    pass


class Spitter(Enemy):
    """Mantem distancia e cospe acido no jogador."""

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.fire_timer = random.uniform(0.5, SPITTER_FIRE_RATE)
        self.strafe = random.choice((-1, 1))

    def update(self, dt: float, target) -> list:
        to_player = target.pos - self.pos
        distance = to_player.length()
        if distance > SPITTER_RANGE:
            self.chase(dt, target.pos)
        elif distance < SPITTER_RANGE * 0.6:
            self.chase(dt, target.pos, -0.8)  # recua
        elif distance > 0:
            self.pos += to_player.normalize().rotate(90 * self.strafe) * self.speed * 0.6 * dt  # anda de lado
        self.finish_move(target.pos)

        self.fire_timer -= dt
        if self.fire_timer <= 0 and self.entered and distance > 0:
            self.fire_timer = SPITTER_FIRE_RATE
            play_sound('Shot', 0.12)
            return [Projectile('Spit', tuple(self.pos), to_player, self.name)]
        return []


class Queen(Enemy):
    """Chefe da onda final: dispara rajadas em circulo e chama filhotes."""

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.max_health = self.health
        self.burst_timer = QUEEN_BURST_COOLDOWN
        self.summon_timer = QUEEN_SUMMON_COOLDOWN
        self.spin = 0.0

    def update(self, dt: float, target) -> list:
        self.chase(dt, target.pos)
        self.finish_move(target.pos)
        if not self.entered:
            return []

        spawned = []
        self.burst_timer -= dt
        self.summon_timer -= dt
        if self.burst_timer <= 0:
            self.burst_timer = QUEEN_BURST_COOLDOWN
            self.spin += 18  # cada rajada sai girada, para nao ficar previsivel
            for i in range(QUEEN_BURST_SHOTS):
                direction = Vector2(1, 0).rotate(self.spin + i * 360 / QUEEN_BURST_SHOTS)
                spawned.append(Projectile('Spit', tuple(self.pos), direction, self.name))
            play_sound('WaveStart', 0.25)
        if self.summon_timer <= 0:
            self.summon_timer = QUEEN_SUMMON_COOLDOWN
            for side in (-1, 1):
                spawned.append(Crawler('Crawler', tuple(self.pos + Vector2(0, 50 * side))))
        return spawned

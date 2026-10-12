import random
import sys

import pygame
from pygame import Surface, Vector2

from core.const import (C_CYAN, C_DARK, C_GREEN, C_GREY, C_ORANGE, C_RED, C_WHITE, C_YELLOW, DASH_COOLDOWN,
                        ENEMY_COLOR, MEDKIT_CHANCE, MENU_CONTROLS, RESULT_ABORT, RESULT_DEFEAT, RESULT_VICTORY,
                        WAVE_BONUS, WAVE_INTERMISSION, WAVES, WIN_FPS, WIN_HEIGHT, WIN_WIDTH)
from core.enemy import Enemy, Queen
from core.entity import Entity
from core.entity_factory import EntityFactory
from core.entity_mediator import EntityMediator
from core.medkit import Medkit
from core.particle import Particle, burst
from core.player import Player
from core.projectile import Projectile
from core.resource import load_image, play_music, play_sound
from core.text import draw_text
from core.wave import Wave, WaveBuilder


class Level:

    def __init__(self, window: Surface):
        self.window = window
        self.background = self.build_background()
        self.crosshair = load_image('Crosshair')
        self.player: Player = EntityFactory.get_entity('Player')
        self.entity_list: list[Entity] = [self.player]
        self.particles: list[Particle] = []
        self.waves: list[Wave] = []
        for i, (enemies, interval) in enumerate(WAVES):
            builder = WaveBuilder().set_number(i + 1).set_interval(interval)
            for name, amount in enemies:
                builder.add_enemy(name, amount)
            self.waves.append(builder.build())
        self.wave_index = 0
        self.state = 'intermission'  # 'intermission' -> 'fighting' -> ... -> 'victory' ou 'defeat'
        self.state_timer = WAVE_INTERMISSION
        self.spawn_timer = 0.0
        self.paused = False

    @property
    def wave(self) -> Wave:
        return self.waves[self.wave_index]

    @property
    def enemies_alive(self) -> int:
        return sum(isinstance(ent, Enemy) for ent in self.entity_list)

    @staticmethod
    def build_background() -> Surface:
        tile = load_image('Floor')
        bg = Surface((WIN_WIDTH, WIN_HEIGHT))
        for x in range(0, WIN_WIDTH, tile.get_width()):
            for y in range(0, WIN_HEIGHT, tile.get_height()):
                bg.blit(tile, (x, y))
        pygame.draw.rect(bg, (90, 30, 30), bg.get_rect(), 6)  # borda da arena
        return bg

    def run(self) -> dict:
        clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        play_music('Battle', 0.35)
        play_sound('WaveStart', 0.5)
        while True:
            dt = min(clock.tick(WIN_FPS) / 1000, 0.05)  # limita o dt se a janela travar por um instante

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and self.state in ('intermission', 'fighting'):
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_q and self.paused:
                        pygame.mouse.set_visible(True)
                        return self.result(RESULT_ABORT)

            if not self.paused:
                self.update_state(dt)
                self.update_entities(dt)
                if self.state in ('victory', 'defeat') and self.state_timer <= 0:
                    pygame.mouse.set_visible(True)
                    return self.result(RESULT_VICTORY if self.state == 'victory' else RESULT_DEFEAT)

            self.draw()
            pygame.display.flip()

    def result(self, result: str) -> dict:
        return {'result': result, 'score': self.player.score, 'wave': self.wave.number}

    # ------------------------------------------------------------ logica
    def update_state(self, dt: float):
        self.state_timer -= dt
        if self.state == 'intermission' and self.state_timer <= 0:
            self.state = 'fighting'
            self.spawn_timer = 0
            if self.wave.has_boss:
                play_music('Boss', 0.4)

        elif self.state == 'fighting':
            self.spawn_timer -= dt
            if self.wave.spawn_queue and self.spawn_timer <= 0:
                self.spawn_timer = self.wave.interval
                self.entity_list.append(EntityFactory.get_entity(self.wave.spawn_queue.pop(0)))
            if not self.wave.spawn_queue and self.enemies_alive == 0:
                self.player.score += WAVE_BONUS * self.wave.number
                if self.wave_index == len(self.waves) - 1:
                    self.player.score += self.player.health * 5  # bonus pela vida que sobrou
                    self.state, self.state_timer = 'victory', 2.5
                    pygame.mixer.music.stop()
                    play_sound('Victory', 0.6)
                else:
                    self.wave_index += 1
                    self.state, self.state_timer = 'intermission', WAVE_INTERMISSION
                    play_sound('WaveStart', 0.5)

        if self.player.health <= 0 and self.state != 'defeat':
            self.state, self.state_timer = 'defeat', 2.0
            self.particles += burst(self.player.pos, C_RED, 40)
            pygame.mixer.music.stop()
            play_sound('GameOver', 0.6)

    def update_entities(self, dt: float):
        mouse = Vector2(pygame.mouse.get_pos())
        for ent in self.entity_list[:]:
            if isinstance(ent, Player) and self.state == 'defeat':
                continue
            target = mouse if isinstance(ent, Player) else self.player
            self.entity_list.extend(ent.update(dt, target))
            ent.flash = max(0.0, ent.flash - dt)

        if self.state != 'defeat':
            EntityMediator.verify_collision(self.entity_list)
        for enemy in EntityMediator.verify_health(self.entity_list):
            size = 60 if isinstance(enemy, Queen) else 14
            self.particles += burst(enemy.pos, ENEMY_COLOR[enemy.name], size)
            play_sound('EnemyDie', 0.35)
            if random.random() < MEDKIT_CHANCE or isinstance(enemy, Queen):
                self.entity_list.append(EntityFactory.get_entity('Medkit', tuple(enemy.pos)))

        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    # ------------------------------------------------------------ desenho
    def draw(self):
        self.window.blit(self.background, (0, 0))
        order = (Medkit, Enemy, Projectile, Player)  # o que vem antes fica por baixo
        for kind in order:
            for ent in self.entity_list:
                if isinstance(ent, kind) and not (isinstance(ent, Player) and self.state == 'defeat'):
                    ent.draw(self.window)
        for particle in self.particles:
            particle.draw(self.window)
        self.draw_hud()
        self.draw_banner()
        if self.paused:
            self.draw_pause()
        else:
            self.window.blit(self.crosshair, self.crosshair.get_rect(center=pygame.mouse.get_pos()))

    def draw_bar(self, pos: tuple, size: tuple, ratio: float, color: tuple):
        x, y = pos
        w, h = size
        pygame.draw.rect(self.window, C_DARK, (x - 2, y - 2, w + 4, h + 4))
        pygame.draw.rect(self.window, (60, 60, 70), (x, y, w, h))
        pygame.draw.rect(self.window, color, (x, y, int(w * max(0.0, min(1.0, ratio))), h))

    def draw_hud(self):
        player = self.player
        ratio = player.health / player.max_health
        color = C_GREEN if ratio > 0.5 else C_YELLOW if ratio > 0.25 else C_RED
        self.draw_bar((16, 16), (200, 16), ratio, color)
        draw_text(self.window, f'VIDA {max(0, player.health)}', 16, color, (226, 15), 'topleft')
        dash_ready = 1 - player.dash_cooldown / DASH_COOLDOWN
        self.draw_bar((16, 40), (200, 8), dash_ready, C_CYAN if dash_ready >= 1 else C_GREY)
        draw_text(self.window, 'ESQUIVA PRONTA' if dash_ready >= 1 else 'ESQUIVA...', 12, C_CYAN, (16, 52),
                  'topleft')

        draw_text(self.window, f'ONDA {self.wave.number}/{len(self.waves)}', 22, C_ORANGE, (WIN_WIDTH / 2, 20))
        remaining = len(self.wave.spawn_queue) + self.enemies_alive
        draw_text(self.window, f'Insetos restantes: {remaining}', 14, C_WHITE, (WIN_WIDTH / 2, 44))
        draw_text(self.window, f'PONTOS {player.score}', 22, C_YELLOW, (WIN_WIDTH - 16, 12), 'topright')

        for ent in self.entity_list:
            if isinstance(ent, Queen):
                draw_text(self.window, 'RAINHA DA COLMEIA', 16, C_RED, (WIN_WIDTH / 2, WIN_HEIGHT - 46))
                self.draw_bar((WIN_WIDTH / 2 - 250, WIN_HEIGHT - 32), (500, 14), ent.health / ent.max_health,
                              C_RED)

    def draw_banner(self):
        center = (WIN_WIDTH / 2, WIN_HEIGHT / 2 - 40)
        if self.state == 'intermission':
            title = 'ONDA FINAL' if self.wave.has_boss else f'ONDA {self.wave.number}'
            draw_text(self.window, title, 56, C_ORANGE, center)
            draw_text(self.window, f'comeca em {max(0.0, self.state_timer):.0f}...', 20, C_WHITE,
                      (center[0], center[1] + 50))
            if self.wave.number == 1:
                draw_text(self.window, 'Sobreviva as 5 ondas para vencer!', 18, C_YELLOW,
                          (center[0], center[1] + 85))
        elif self.state == 'victory':
            draw_text(self.window, 'ARENA LIMPA!', 60, C_GREEN, center)
        elif self.state == 'defeat':
            draw_text(self.window, 'VOCE CAIU...', 60, C_RED, center)

    def draw_pause(self):
        shade = Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        self.window.blit(shade, (0, 0))
        draw_text(self.window, 'PAUSADO', 56, C_YELLOW, (WIN_WIDTH / 2, 170))
        for i, line in enumerate(MENU_CONTROLS):
            draw_text(self.window, line, 18, C_WHITE, (WIN_WIDTH / 2 - 190, 250 + i * 30), 'topleft')
        draw_text(self.window, 'ESC - continuar      Q - sair para o menu', 20, C_ORANGE, (WIN_WIDTH / 2, 450))

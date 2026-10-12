import sys

import pygame
from pygame import Surface

from core.const import C_GREY, C_ORANGE, C_WHITE, C_YELLOW, MENU_CONTROLS, MENU_OPTION, WIN_HEIGHT, WIN_WIDTH
from core.resource import load_image, play_music, play_sound
from core.text import draw_text


class Menu:

    def __init__(self, window: Surface):
        self.window = window
        self.surf = load_image('MenuBg')
        self.rect = self.surf.get_rect(left=0, top=0)

    def run(self) -> str:
        option = 0
        play_music('Menu', 0.4)
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            # desenha
            self.window.blit(self.surf, self.rect)
            draw_text(self.window, 'BUG SIEGE', 84, C_ORANGE, (WIN_WIDTH / 2, 110))
            draw_text(self.window, 'sobreviva a infestacao', 20, C_GREY, (WIN_WIDTH / 2, 170))

            for i, text in enumerate(MENU_OPTION):
                selected = i == option
                label = f'> {text} <' if selected else text
                draw_text(self.window, label, 30, C_YELLOW if selected else C_WHITE, (WIN_WIDTH / 2, 250 + 50 * i))

            box = pygame.Rect(0, 0, 470, 200)
            box.midbottom = (WIN_WIDTH / 2, WIN_HEIGHT - 30)
            panel = Surface(box.size, pygame.SRCALPHA)
            panel.fill((0, 0, 0, 150))
            self.window.blit(panel, box)
            pygame.draw.rect(self.window, C_ORANGE, box, 2)
            draw_text(self.window, 'COMANDOS', 18, C_ORANGE, (box.centerx, box.top + 20))
            for i, line in enumerate(MENU_CONTROLS):
                draw_text(self.window, line, 16, C_WHITE, (box.left + 30, box.top + 45 + 28 * i), 'topleft')
            draw_text(self.window, 'Setas + ENTER para escolher', 14, C_GREY, (WIN_WIDTH / 2, box.top - 16))
            pygame.display.flip()

            # eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        option = (option + 1) % len(MENU_OPTION)  # menu circular
                        play_sound('Hit', 0.2)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        option = (option - 1) % len(MENU_OPTION)
                        play_sound('Hit', 0.2)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        play_sound('Pickup', 0.4)
                        return MENU_OPTION[option]

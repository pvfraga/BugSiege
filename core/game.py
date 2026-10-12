import sys

import pygame

from core.const import MENU_OPTION, RESULT_ABORT, WIN_HEIGHT, WIN_TITLE, WIN_WIDTH
from core.level import Level
from core.menu import Menu
from core.score import Score


class Game:

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass  # sem placa de som: o jogo roda mudo
        self.window = pygame.display.set_mode(size=(WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption(WIN_TITLE)

    def run(self):
        while True:
            score = Score(self.window)
            menu_return = Menu(self.window).run()

            if menu_return == MENU_OPTION[0]:  # JOGAR
                result = Level(self.window).run()
                if result['result'] != RESULT_ABORT:
                    score.save(result)
            elif menu_return == MENU_OPTION[1]:  # RECORDES
                score.show()
            elif menu_return == MENU_OPTION[2]:  # SAIR
                pygame.quit()
                sys.exit()

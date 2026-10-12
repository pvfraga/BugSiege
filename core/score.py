import os
import sys
from datetime import datetime

import pygame
from pygame import Surface

from core.const import (C_GREEN, C_GREY, C_ORANGE, C_RED, C_WHITE, C_YELLOW, NAME_LENGTH, RECORDS_LIMIT,
                        RESULT_VICTORY, WIN_WIDTH)
from core.db_proxy import DBProxy
from core.resource import base_dir, load_image, play_music
from core.text import draw_text

DB_NAME = 'records.db'


def db_path() -> str:
    return os.path.join(base_dir(), DB_NAME)


def get_formatted_date() -> str:
    return datetime.now().strftime('%H:%M - %d/%m/%y')


class Score:

    def __init__(self, window: Surface):
        self.window = window
        self.surf = load_image('RecordsBg')
        self.rect = self.surf.get_rect(left=0, top=0)

    @staticmethod
    def check_quit(event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def save(self, result: dict):
        """Tela de fim de partida: mostra o resultado e pede as iniciais para o recorde."""
        play_music('Menu', 0.3)
        name = ''
        clock = pygame.time.Clock()
        victory = result['result'] == RESULT_VICTORY
        while True:
            clock.tick(30)
            self.window.blit(self.surf, self.rect)
            if victory:
                draw_text(self.window, 'VITORIA!', 72, C_GREEN, (WIN_WIDTH / 2, 110))
                draw_text(self.window, 'Voce sobreviveu as 5 ondas e derrotou a Rainha!', 20, C_WHITE,
                          (WIN_WIDTH / 2, 170))
            else:
                draw_text(self.window, 'GAME OVER', 72, C_RED, (WIN_WIDTH / 2, 110))
                draw_text(self.window, f'Voce caiu na onda {result["wave"]}.', 20, C_WHITE, (WIN_WIDTH / 2, 170))

            draw_text(self.window, f'PONTUACAO: {result["score"]}', 36, C_YELLOW, (WIN_WIDTH / 2, 240))
            draw_text(self.window, f'Digite suas iniciais ({NAME_LENGTH} letras):', 22, C_WHITE,
                      (WIN_WIDTH / 2, 320))
            slots = ' '.join(name[i] if i < len(name) else '_' for i in range(NAME_LENGTH))
            draw_text(self.window, slots, 56, C_ORANGE, (WIN_WIDTH / 2, 385))
            draw_text(self.window, 'ENTER - salvar     BACKSPACE - apagar     ESC - nao salvar', 16, C_GREY,
                      (WIN_WIDTH / 2, 470))
            pygame.display.flip()

            for event in pygame.event.get():
                self.check_quit(event)
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and len(name) == NAME_LENGTH:
                    db_proxy = DBProxy(db_path())
                    db_proxy.save({'name': name, 'score': result['score'], 'wave': result['wave'],
                                   'result': result['result'], 'date': get_formatted_date()})
                    db_proxy.close()
                    self.show()
                    return
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < NAME_LENGTH and event.unicode.isalnum() and event.unicode.isascii():
                    name += event.unicode.upper()

    def show(self):
        """Tabela com os melhores resultados salvos no banco."""
        play_music('Menu', 0.3)
        db_proxy = DBProxy(db_path())
        records = db_proxy.retrieve_top(RECORDS_LIMIT)
        db_proxy.close()

        columns = (('#', 150), ('NOME', 220), ('PONTOS', 340), ('ONDA', 460), ('RESULTADO', 590), ('DATA', 760))
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            self.window.blit(self.surf, self.rect)
            draw_text(self.window, f'TOP {RECORDS_LIMIT} RECORDES', 48, C_YELLOW, (WIN_WIDTH / 2, 60))
            for title, x in columns:
                draw_text(self.window, title, 18, C_ORANGE, (x, 130))
            if not records:
                draw_text(self.window, 'Nenhum recorde ainda. Va jogar!', 22, C_WHITE, (WIN_WIDTH / 2, 300))
            for i, (name, score, wave, result, date) in enumerate(records):
                y = 170 + i * 38
                color = C_GREEN if result == RESULT_VICTORY else C_WHITE
                for value, (_, x) in zip((f'{i + 1}', name, score, wave, result, date), columns):
                    draw_text(self.window, str(value), 18, color, (x, y))
            draw_text(self.window, 'ESC / ENTER - voltar ao menu', 16, C_GREY, (WIN_WIDTH / 2, 610))
            pygame.display.flip()

            for event in pygame.event.get():
                self.check_quit(event)
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN,
                                                                  pygame.K_KP_ENTER):
                    return

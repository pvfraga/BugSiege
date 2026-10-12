import random

from core.const import WIN_HEIGHT, WIN_WIDTH
from core.enemy import Brute, Crawler, Queen, Spitter
from core.entity import Entity
from core.medkit import Medkit
from core.player import Player

ENEMY_CLASS = {
    'Crawler': Crawler,
    'Brute': Brute,
    'Spitter': Spitter,
    'Queen': Queen,
}


class EntityFactory:
    """Padrao Factory: o resto do jogo pede uma entidade pelo nome e nao precisa
    saber qual classe instanciar nem onde ela deve nascer."""

    @staticmethod
    def get_entity(entity_name: str, position: tuple | None = None) -> Entity:
        match entity_name:
            case 'Player':
                return Player('Player', position or (WIN_WIDTH / 2, WIN_HEIGHT / 2))
            case 'Medkit':
                return Medkit('Medkit', position)
            case name if name in ENEMY_CLASS:
                return ENEMY_CLASS[name](name, position or EntityFactory.edge_position())
            case _:
                raise ValueError(f'Entidade desconhecida: {entity_name}')

    @staticmethod
    def edge_position(margin: int = 60) -> tuple:
        """Sorteia um ponto logo fora de uma das 4 bordas da arena."""
        side = random.choice(('top', 'bottom', 'left', 'right'))
        if side == 'top':
            return random.randint(0, WIN_WIDTH), -margin
        if side == 'bottom':
            return random.randint(0, WIN_WIDTH), WIN_HEIGHT + margin
        if side == 'left':
            return -margin, random.randint(0, WIN_HEIGHT)
        return WIN_WIDTH + margin, random.randint(0, WIN_HEIGHT)

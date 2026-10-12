from core.const import ENTITY_SCORE, MEDKIT_HEAL, WIN_HEIGHT, WIN_WIDTH
from core.enemy import Enemy
from core.entity import Entity
from core.medkit import Medkit
from core.player import Player
from core.projectile import Projectile
from core.resource import play_sound


class EntityMediator:
    """Padrao Mediator: as entidades nao conversam entre si. Toda interacao
    (colisao, dano, pontuacao, remocao) passa por aqui."""

    @staticmethod
    def collide(rect_a, rect_b) -> bool:
        """Colisao por hitbox retangular, respondendo as 4 perguntas:
        direita de A passa a esquerda de B? esquerda de A antes da direita de B?
        base de A abaixo do topo de B? topo de A acima da base de B?"""
        return (rect_a.right >= rect_b.left and
                rect_a.left <= rect_b.right and
                rect_a.bottom >= rect_b.top and
                rect_a.top <= rect_b.bottom)

    @staticmethod
    def __verify_collision_window(ent: Entity):
        # projetil que saiu da tela nao serve mais: zera a vida para ser removido
        if isinstance(ent, Projectile):
            if ent.rect.right < 0 or ent.rect.left > WIN_WIDTH or ent.rect.bottom < 0 or ent.rect.top > WIN_HEIGHT:
                ent.health = 0

    @staticmethod
    def __verify_collision_entity(ent1: Entity, ent2: Entity):
        # coloca sempre na mesma ordem para reduzir a quantidade de casos
        if isinstance(ent2, Player) or (isinstance(ent2, Projectile) and isinstance(ent1, Enemy)):
            ent1, ent2 = ent2, ent1

        valid = (
            (isinstance(ent1, Projectile) and ent1.owner == 'Player' and isinstance(ent2, Enemy)) or
            (isinstance(ent1, Player) and isinstance(ent2, Projectile) and ent2.owner != 'Player') or
            (isinstance(ent1, Player) and isinstance(ent2, (Enemy, Medkit)))
        )
        if not valid or ent1.health <= 0 or ent2.health <= 0:
            return
        if not EntityMediator.collide(ent1.hitbox, ent2.hitbox):
            return

        if isinstance(ent1, Projectile):  # tiro do jogador acertou um inseto
            ent2.take_damage(ent1.damage, ent1.owner)
            ent1.health = 0
            play_sound('Hit', 0.3)
        elif isinstance(ent2, Medkit):
            ent1.heal(MEDKIT_HEAL)
            ent2.health = 0
            play_sound('Pickup', 0.5)
        elif isinstance(ent2, Projectile):  # cuspe acertou o jogador (a esquiva atravessa)
            if not ent1.is_invulnerable:
                ent1.take_damage(ent2.damage, ent2.owner)
                ent2.health = 0
        else:  # inseto encostou no jogador
            ent1.take_damage(ent2.damage, ent2.name)

    @staticmethod
    def __separate_enemies(ent1: Entity, ent2: Entity):
        """Empurra dois insetos sobrepostos para nao virarem um bolo so."""
        if not (isinstance(ent1, Enemy) and isinstance(ent2, Enemy)):
            return
        delta = ent1.pos - ent2.pos
        min_dist = (ent1.hitbox.width + ent2.hitbox.width) / 2
        dist = delta.length()
        if 0 < dist < min_dist:
            push = delta.normalize() * (min_dist - dist) / 2
            ent1.pos += push
            ent2.pos -= push

    @staticmethod
    def verify_collision(entity_list: list[Entity]):
        for i in range(len(entity_list)):
            ent1 = entity_list[i]
            EntityMediator.__verify_collision_window(ent1)
            for j in range(i + 1, len(entity_list)):  # i + 1: nao compara consigo nem repete pares
                ent2 = entity_list[j]
                EntityMediator.__verify_collision_entity(ent1, ent2)
                EntityMediator.__separate_enemies(ent1, ent2)

    @staticmethod
    def __give_score(enemy: Enemy, entity_list: list[Entity]):
        if enemy.last_dmg != 'Player':
            return
        for ent in entity_list:
            if isinstance(ent, Player):
                ent.score += ENTITY_SCORE[enemy.name]

    @staticmethod
    def verify_health(entity_list: list[Entity]) -> list[Enemy]:
        """Remove quem ficou sem vida e devolve os insetos derrotados (para efeitos e drops)."""
        killed = []
        for ent in entity_list[:]:  # copia: nao se remove item da lista que esta sendo percorrida
            if ent.health <= 0 and not isinstance(ent, Player):
                if isinstance(ent, Enemy):
                    EntityMediator.__give_score(ent, entity_list)
                    killed.append(ent)
                entity_list.remove(ent)
        return killed

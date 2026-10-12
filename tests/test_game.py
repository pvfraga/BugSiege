import os
import sys

import pygame
import pytest
from pygame import Vector2

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.const import ENTITY_HEALTH, ENTITY_SCORE, MEDKIT_HEAL  # noqa: E402
from core.db_proxy import DBProxy  # noqa: E402
from core.entity_factory import EntityFactory  # noqa: E402
from core.entity_mediator import EntityMediator  # noqa: E402
from core.projectile import Projectile  # noqa: E402
from core.wave import WaveBuilder  # noqa: E402


@pytest.fixture(scope='module', autouse=True)
def screen():
    pygame.init()
    pygame.display.set_mode((10, 10))  # convert_alpha precisa de uma janela
    yield
    pygame.quit()


def test_collide_overlapping_and_apart():
    a = pygame.Rect(0, 0, 10, 10)
    assert EntityMediator.collide(a, pygame.Rect(5, 5, 10, 10))
    assert not EntityMediator.collide(a, pygame.Rect(30, 0, 10, 10))
    assert not EntityMediator.collide(a, pygame.Rect(0, 30, 10, 10))


def test_bullet_damages_enemy_and_gives_score():
    player = EntityFactory.get_entity('Player', (100, 100))
    crawler = EntityFactory.get_entity('Crawler', (300, 300))
    entities = [player, crawler]
    for _ in range(ENTITY_HEALTH['Crawler'] // 10):
        entities.append(Projectile('Bullet', (300, 300), Vector2(1, 0), 'Player'))
        EntityMediator.verify_collision(entities)
        killed = EntityMediator.verify_health(entities)
    assert killed == [crawler]
    assert crawler not in entities
    assert player.score == ENTITY_SCORE['Crawler']


def test_spit_does_not_hit_player_during_dash():
    player = EntityFactory.get_entity('Player', (100, 100))
    player.dash_timer = 0.1
    spit = Projectile('Spit', (100, 100), Vector2(1, 0), 'Spitter')
    EntityMediator.verify_collision([player, spit])
    assert player.health == ENTITY_HEALTH['Player']
    assert spit.health > 0


def test_medkit_heals_but_not_above_max():
    player = EntityFactory.get_entity('Player', (100, 100))
    player.health = 90
    EntityMediator.verify_collision([player, EntityFactory.get_entity('Medkit', (100, 100))])
    assert player.health == min(ENTITY_HEALTH['Player'], 90 + MEDKIT_HEAL)


def test_projectile_out_of_window_is_removed():
    bullet = Projectile('Bullet', (-50, -50), Vector2(1, 0), 'Player')
    entities = [bullet]
    EntityMediator.verify_collision(entities)
    EntityMediator.verify_health(entities)
    assert entities == []


def test_wave_builder_puts_boss_first():
    wave = WaveBuilder().set_number(5).add_enemy('Crawler', 4).add_enemy('Queen', 1).set_interval(0.5).build()
    assert wave.spawn_queue[0] == 'Queen'
    assert len(wave.spawn_queue) == 5
    assert wave.has_boss and wave.interval == pytest.approx(0.5)


def test_db_proxy_orders_by_score(tmp_path):
    db = DBProxy(str(tmp_path / 'test.db'))
    for name, score in (('AAA', 100), ('BBB', 300), ('CCC', 200)):
        db.save({'name': name, 'score': score, 'wave': 1, 'result': 'DERROTA', 'date': '-'})
    assert [row[0] for row in db.retrieve_top(2)] == ['BBB', 'CCC']
    db.close()

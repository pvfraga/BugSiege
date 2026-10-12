# C
C_WHITE = (240, 240, 240)
C_GREY = (150, 150, 160)
C_DARK = (20, 22, 30)
C_YELLOW = (255, 214, 64)
C_ORANGE = (255, 140, 40)
C_RED = (230, 60, 60)
C_GREEN = (90, 220, 110)
C_CYAN = (80, 220, 230)
C_PURPLE = (190, 110, 255)

# D
DASH_COOLDOWN = 2.0  # segundos
DASH_DURATION = 0.18
DASH_MULTIPLIER = 3.2

# E
ENTITY_SPEED = {  # pixels por segundo
    'Player': 230,
    'Crawler': 145,
    'Brute': 70,
    'Spitter': 95,
    'Queen': 55,
    'Bullet': 640,
    'Spit': 270,
    'Medkit': 0,
}

ENTITY_HEALTH = {
    'Player': 100,
    'Crawler': 20,
    'Brute': 90,
    'Spitter': 35,
    'Queen': 1000,
    'Bullet': 1,
    'Spit': 1,
    'Medkit': 1,
}

ENTITY_DAMAGE = {  # dano causado ao colidir
    'Player': 1,
    'Crawler': 10,
    'Brute': 25,
    'Spitter': 8,
    'Queen': 30,
    'Bullet': 10,
    'Spit': 12,
    'Medkit': 0,
}

ENTITY_SCORE = {  # pontos ao derrotar o inimigo
    'Crawler': 10,
    'Brute': 35,
    'Spitter': 25,
    'Queen': 500,
}

ENEMY_COLOR = {  # cor das particulas ao morrer
    'Crawler': (120, 230, 90),
    'Brute': (210, 120, 60),
    'Spitter': (200, 90, 230),
    'Queen': (255, 70, 110),
}

# H
HITBOX_SCALE = 0.7  # hitbox menor que o desenho, para colisao mais justa

# M
MEDKIT_CHANCE = 0.08
MEDKIT_HEAL = 25
MEDKIT_LIFETIME = 9.0

MENU_OPTION = ('JOGAR', 'RECORDES', 'SAIR')

MENU_CONTROLS = (
    'W A S D  - Mover',
    'Mouse    - Mirar',
    'Clique / Espaco - Atirar',
    'Shift    - Esquiva (invulneravel)',
    'ESC      - Pausar',
)

# N
NAME_LENGTH = 3

# P
PLAYER_FIRE_RATE = 0.16  # segundos entre tiros
PLAYER_INVULNERABLE_TIME = 0.7

# Q
QUEEN_BURST_COOLDOWN = 3.0
QUEEN_BURST_SHOTS = 10
QUEEN_SUMMON_COOLDOWN = 4.5

# R
RECORDS_LIMIT = 10
RESULT_VICTORY = 'VITORIA'
RESULT_DEFEAT = 'DERROTA'
RESULT_ABORT = 'ABORT'

# S
SPITTER_RANGE = 260
SPITTER_FIRE_RATE = 1.8

# W
WAVE_INTERMISSION = 3.0
WAVE_BONUS = 100  # bonus por onda concluida (multiplicado pelo numero da onda)
WIN_WIDTH = 960
WIN_HEIGHT = 640
WIN_FPS = 60
WIN_TITLE = 'Bug Siege'

# ondas: (lista de (inimigo, quantidade), intervalo entre spawns em segundos)
WAVES = (
    ((('Crawler', 8),), 1.0),
    ((('Crawler', 10), ('Spitter', 3)), 0.9),
    ((('Crawler', 12), ('Brute', 3), ('Spitter', 4)), 0.8),
    ((('Crawler', 16), ('Brute', 5), ('Spitter', 6)), 0.65),
    ((('Queen', 1), ('Crawler', 8), ('Brute', 2)), 0.9),
)

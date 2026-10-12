"""Gera todas as imagens (PNG) e sons (WAV) do jogo na pasta asset/.

Rodar uma vez a partir da raiz do projeto:  python tools/generate_assets.py
Nenhum arquivo e baixado da internet: tudo e desenhado/sintetizado aqui.
"""
import os
import random
import struct
import wave

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(ROOT, 'asset')
SAMPLE_RATE = 22050

random.seed(42)


# ---------------------------------------------------------------- imagens
def new_surface(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def save(surface, name, scale=1):
    if scale != 1:
        size = (surface.get_width() * scale, surface.get_height() * scale)
        surface = pygame.transform.scale(surface, size)  # nearest: mantem o pixel art
    pygame.image.save(surface, os.path.join(ASSET_DIR, name))


def draw_player():
    s = new_surface(22, 22)
    pygame.draw.rect(s, (40, 40, 45), (12, 9, 10, 4))          # cano da arma
    pygame.draw.rect(s, (90, 90, 100), (12, 10, 8, 2))
    pygame.draw.ellipse(s, (50, 80, 55), (3, 3, 13, 16))       # ombros
    pygame.draw.ellipse(s, (70, 110, 75), (4, 4, 11, 14))
    pygame.draw.circle(s, (35, 60, 40), (10, 11), 5)           # capacete
    pygame.draw.circle(s, (60, 95, 65), (10, 11), 4)
    pygame.draw.rect(s, (80, 220, 230), (12, 9, 2, 4))         # visor
    pygame.draw.circle(s, (230, 190, 150), (14, 15), 2)        # mao
    save(s, 'Player.png', 2)


def draw_bug(name, size, body, dark, legs, eye, extra=None):
    s = new_surface(size, size)
    c = size // 2
    for i in (-1, 0, 1):  # 3 pares de pernas
        x = c + i * size // 6
        pygame.draw.line(s, legs, (x, c), (x - size // 8, 1), 1)
        pygame.draw.line(s, legs, (x, c), (x - size // 8, size - 2), 1)
    pygame.draw.ellipse(s, dark, (1, c - size // 4, size - size // 3, size // 2))  # abdomen
    pygame.draw.ellipse(s, body, (2, c - size // 4 + 1, size - size // 3 - 2, size // 2 - 2))
    pygame.draw.circle(s, dark, (size - size // 4, c), size // 6 + 1)               # cabeca
    pygame.draw.circle(s, body, (size - size // 4, c), size // 6)
    pygame.draw.line(s, legs, (size - size // 6, c - 2), (size - 1, c - size // 5), 1)  # mandibulas
    pygame.draw.line(s, legs, (size - size // 6, c + 2), (size - 1, c + size // 5), 1)
    pygame.draw.circle(s, eye, (size - size // 4 + 1, c - 2), 1)
    pygame.draw.circle(s, eye, (size - size // 4 + 1, c + 2), 1)
    if extra:
        extra(s, size, c)
    return s


def brute_plates(s, size, c):
    for x in range(5, size - size // 3 - 2, 5):
        pygame.draw.line(s, (90, 50, 25), (x, c - size // 4 + 2), (x, c + size // 4 - 2), 2)


def spitter_sac(s, size, c):
    pygame.draw.circle(s, (120, 230, 120), (size // 3, c), size // 6)
    pygame.draw.circle(s, (190, 255, 170), (size // 3 - 1, c - 1), size // 12)


def queen_crown(s, size, c):
    brute_plates(s, size, c)
    head_x = size - size // 4
    for dy in (-8, -4, 0, 4, 8):
        spike = [(head_x - 3, c + dy), (head_x - 10, c + dy - 2), (head_x - 10, c + dy + 2)]
        pygame.draw.polygon(s, (255, 210, 80), spike)
    pygame.draw.circle(s, (255, 230, 120), (size // 3, c), 3)


def draw_items():
    s = new_surface(6, 2)
    s.fill((255, 230, 120))
    s.set_at((5, 0), (255, 255, 230))
    s.set_at((5, 1), (255, 255, 230))
    save(s, 'Bullet.png', 2)

    s = new_surface(7, 7)
    pygame.draw.circle(s, (120, 40, 150), (3, 3), 3)
    pygame.draw.circle(s, (170, 255, 110), (3, 3), 2)
    s.set_at((2, 2), (240, 255, 220))
    save(s, 'Spit.png', 2)

    s = new_surface(11, 11)
    pygame.draw.rect(s, (230, 230, 230), (0, 1, 11, 10), border_radius=2)
    pygame.draw.rect(s, (160, 160, 170), (0, 1, 11, 10), 1, border_radius=2)
    pygame.draw.rect(s, (220, 40, 50), (4, 3, 3, 7))
    pygame.draw.rect(s, (220, 40, 50), (2, 5, 7, 3))
    save(s, 'Medkit.png', 2)

    s = new_surface(25, 25)
    pygame.draw.circle(s, (255, 255, 255), (12, 12), 9, 2)
    for a, b in (((12, 0), (12, 6)), ((12, 18), (12, 24)), ((0, 12), (6, 12)), ((18, 12), (24, 12))):
        pygame.draw.line(s, (255, 80, 80), a, b, 2)
    save(s, 'Crosshair.png')


def floor_tile():
    s = pygame.Surface((32, 32))
    s.fill((46, 50, 58))
    for _ in range(60):  # ruido de textura
        x, y = random.randrange(32), random.randrange(32)
        v = random.randint(38, 56)
        s.set_at((x, y), (v, v + 3, v + 9))
    pygame.draw.rect(s, (30, 33, 40), (0, 0, 32, 32), 1)
    pygame.draw.line(s, (62, 67, 77), (1, 1), (30, 1))
    for p in ((3, 3), (28, 3), (3, 28), (28, 28)):  # rebites
        s.set_at(p, (80, 86, 98))
    return s


def background(name, tint, splat_colors, seed):
    rnd = random.Random(seed)
    tile = pygame.transform.scale(floor_tile(), (64, 64))
    s = pygame.Surface((960, 640))
    for x in range(0, 960, 64):
        for y in range(0, 640, 64):
            s.blit(tile, (x, y))
    stains = new_surface(960, 640)
    for _ in range(26):  # manchas de gosma
        color = rnd.choice(splat_colors) + (90,)
        cx, cy = rnd.randrange(960), rnd.randrange(640)
        for _ in range(7):
            r = rnd.randint(4, 18)
            pygame.draw.circle(stains, color, (cx + rnd.randint(-22, 22), cy + rnd.randint(-22, 22)), r)
    s.blit(stains, (0, 0))
    shade = new_surface(960, 640)
    for i in range(40):  # vinheta
        alpha = int(150 * (i / 40) ** 2)
        pygame.draw.rect(shade, tint + (alpha // 8,), (i * 6, i * 4, 960 - i * 12, 640 - i * 8), 6)
    s.blit(shade, (0, 0))
    overlay = new_surface(960, 640)
    overlay.fill(tint + (60,))
    s.blit(overlay, (0, 0))
    pygame.image.save(s, os.path.join(ASSET_DIR, name))


def make_images():
    draw_player()
    bugs = (  # nome, tamanho, cor, contorno, pernas, olhos, detalhe extra
        ('Crawler', 17, (110, 200, 80), (50, 100, 40), (40, 70, 30), (255, 60, 60), None),
        ('Brute', 27, (180, 110, 60), (100, 60, 30), (70, 40, 20), (255, 220, 60), brute_plates),
        ('Spitter', 19, (170, 80, 210), (90, 40, 120), (60, 30, 80), (200, 255, 120), spitter_sac),
        ('Queen', 55, (220, 60, 100), (120, 20, 50), (80, 10, 30), (255, 255, 120), queen_crown),
    )
    for name, *params in bugs:
        save(draw_bug(name, *params), f'{name}.png', 2)
    draw_items()
    pygame.image.save(pygame.transform.scale(floor_tile(), (64, 64)), os.path.join(ASSET_DIR, 'Floor.png'))
    background('MenuBg.png', (10, 10, 30), [(90, 200, 60), (160, 60, 200), (200, 40, 60)], 7)
    background('RecordsBg.png', (25, 10, 40), [(160, 60, 200), (90, 60, 200)], 11)


# ---------------------------------------------------------------- sons
def write_wav(name, samples):
    with wave.open(os.path.join(ASSET_DIR, name), 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        frames = b''.join(struct.pack('<h', int(max(-1.0, min(1.0, v)) * 30000)) for v in samples)
        f.writeframes(frames)


def square(phase):
    return 1.0 if (phase % 1.0) < 0.5 else -1.0


def triangle(phase):
    p = phase % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


def sweep(duration, f_start, f_end, wave_fn=square, volume=0.5, noise=0.0):
    n = int(duration * SAMPLE_RATE)
    out, phase = [], 0.0
    for i in range(n):
        t = i / n
        freq = f_start + (f_end - f_start) * t
        phase += freq / SAMPLE_RATE
        env = (1 - t) ** 1.5
        v = wave_fn(phase) * (1 - noise) + random.uniform(-1, 1) * noise
        out.append(v * env * volume)
    return out


def notes_to_samples(notes, wave_fn, volume, step):
    """notes: lista de frequencias (0 = pausa), cada uma dura 'step' segundos."""
    out = []
    for freq in notes:
        n = int(step * SAMPLE_RATE)
        phase = 0.0
        for i in range(n):
            phase += freq / SAMPLE_RATE
            env = min(1.0, i / 200) * (1 - i / n) ** 0.6
            out.append(wave_fn(phase) * env * volume if freq else 0.0)
    return out


def note(name):
    names = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
    if name == '-':
        return 0
    base, octave = name[0], int(name[-1])
    semi = names[base] + (1 if '#' in name else 0) + (octave - 4) * 12
    return 440.0 * 2 ** (semi / 12)


def mix(*tracks):
    size = max(len(t) for t in tracks)
    return [sum(t[i] if i < len(t) else 0.0 for t in tracks) for i in range(size)]


def song(melody, bass, step, repeats, lead=square, lead_vol=0.18, bass_vol=0.22, drums=True):
    m = notes_to_samples([note(n) for n in melody] * repeats, lead, lead_vol, step)
    b = notes_to_samples([note(n) for n in bass] * repeats, triangle, bass_vol, step * 2)
    tracks = [m, b]
    if drums:
        kick = sweep(0.09, 150, 40, triangle, 0.5)
        hat = sweep(0.03, 8000, 8000, square, 0.08, noise=1.0)
        d = [0.0] * len(m)
        beat = int(step * 2 * SAMPLE_RATE)
        for k, start in enumerate(range(0, len(d), beat)):
            sample = kick if k % 2 == 0 else hat
            for j, v in enumerate(sample):
                if start + j < len(d):
                    d[start + j] += v
        tracks.append(d)
    return mix(*tracks)


def make_sounds():
    write_wav('Shot.wav', sweep(0.09, 1100, 300, square, 0.35, noise=0.25))
    write_wav('Hit.wav', sweep(0.06, 400, 200, square, 0.35, noise=0.8))
    write_wav('EnemyDie.wav', sweep(0.28, 260, 50, square, 0.45, noise=0.55))
    write_wav('PlayerHurt.wav', sweep(0.3, 220, 80, square, 0.5, noise=0.2))
    write_wav('Dash.wav', sweep(0.2, 300, 1400, triangle, 0.45, noise=0.5))
    write_wav('Pickup.wav', notes_to_samples([note('C5'), note('E5'), note('G5'), note('C6')], square, 0.3, 0.06))
    write_wav('WaveStart.wav', notes_to_samples([note('A4'), note('E5'), note('A4'), note('E5')], square, 0.3, 0.12))
    write_wav('Victory.wav', notes_to_samples(
        [note(n) for n in ('C5', 'E5', 'G5', 'C6', '-', 'G5', 'C6', 'C6')], square, 0.3, 0.16))
    write_wav('GameOver.wav', notes_to_samples(
        [note(n) for n in ('E5', 'D#5', 'D5', 'C#5', 'C5', '-', 'A3', 'A3')], square, 0.3, 0.2))

    menu_melody = ['A4', '-', 'C5', 'E5', 'D5', '-', 'C5', 'B4', 'A4', '-', 'E4', 'G4', 'A4', '-', '-', '-',
                   'F4', '-', 'A4', 'C5', 'B4', '-', 'A4', 'G4', 'E4', '-', 'G4', 'B4', 'A4', '-', '-', '-']
    menu_bass = ['A2', 'A2', 'F2', 'F2', 'C3', 'C3', 'E2', 'E2', 'D2', 'D2', 'F2', 'F2', 'E2', 'E2', 'A2', 'A2']
    write_wav('Menu.wav', song(menu_melody, menu_bass, 0.22, 2, triangle, 0.22, 0.2, drums=False))

    battle_melody = ['E5', 'E5', 'G5', 'E5', 'D5', 'E5', '-', 'B4', 'C5', 'C5', 'D5', 'C5', 'B4', 'G4', '-', 'A4',
                     'E5', 'E5', 'G5', 'A5', 'G5', 'E5', '-', 'D5', 'C5', 'B4', 'A4', 'B4', 'E4', '-', '-', '-']
    battle_bass = ['E2', 'E3', 'C2', 'C3', 'D2', 'D3', 'B1', 'B2', 'E2', 'E3', 'C2', 'C3', 'A1', 'A2', 'B1', 'B2']
    write_wav('Battle.wav', song(battle_melody, battle_bass, 0.13, 4))

    boss_melody = ['A4', 'A4', 'G#4', 'A4', 'C5', 'A4', 'G#4', 'E4', 'F4', 'F4', 'E4', 'F4', 'A4', 'F4', 'E4', 'D4',
                   'A4', 'C5', 'E5', 'D#5', 'E5', 'C5', 'A4', 'G#4', 'A4', '-', 'E4', '-', 'A3', '-', '-', '-']
    boss_bass = ['A1', 'A2', 'A1', 'A2', 'F1', 'F2', 'F1', 'F2', 'D2', 'D2', 'E2', 'E2', 'A1', 'A1', 'E1', 'E2']
    write_wav('Boss.wav', song(boss_melody, boss_bass, 0.12, 4, square, 0.16, 0.26))


if __name__ == '__main__':
    os.makedirs(ASSET_DIR, exist_ok=True)
    pygame.init()
    make_images()
    make_sounds()
    pygame.quit()
    print('Assets gerados em', ASSET_DIR)

import os
import sys

import pygame


def base_dir() -> str:
    """Pasta raiz do jogo.

    Rodando pelo PyCharm: a pasta onde esta o main.py.
    Rodando o .exe gerado pelo PyInstaller: a pasta onde esta o .exe
    (os assets sao copiados ao lado dele, mantendo a hierarquia de pastas).
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def asset_path(file_name: str) -> str:
    return os.path.join(base_dir(), 'asset', file_name)


_image_cache: dict[str, pygame.Surface] = {}
_sound_cache: dict[str, pygame.mixer.Sound | None] = {}


def load_image(name: str) -> pygame.Surface:
    """Carrega asset/<name>.png uma unica vez (tiros sao criados o tempo todo)."""
    if name not in _image_cache:
        _image_cache[name] = pygame.image.load(asset_path(f'{name}.png')).convert_alpha()
    return _image_cache[name]


def play_sound(name: str, volume: float = 0.5):
    """Toca asset/<name>.wav. Se o PC nao tiver saida de audio, o jogo segue sem som."""
    if name not in _sound_cache:
        try:
            sound = pygame.mixer.Sound(asset_path(f'{name}.wav'))
            sound.set_volume(volume)
        except pygame.error:
            sound = None
        _sound_cache[name] = sound
    if _sound_cache[name]:
        _sound_cache[name].play()


def play_music(name: str, volume: float = 0.4):
    try:
        pygame.mixer.music.load(asset_path(f'{name}.wav'))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

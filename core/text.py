import pygame

_font_cache: dict[tuple, pygame.font.Font] = {}


def get_font(size: int, bold: bool = True) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont('consolas, couriernew, monospace', size, bold=bold)
    return _font_cache[key]


def draw_text(window: pygame.Surface, text: str, size: int, color: tuple, pos: tuple,
              anchor: str = 'center', shadow: bool = True) -> pygame.Rect:
    """Escreve um texto na tela. anchor: 'center', 'topleft', 'topright' ou 'midleft'."""
    font = get_font(size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(**{anchor: pos})
    if shadow:
        window.blit(font.render(text, True, (0, 0, 0)), rect.move(2, 2))
    window.blit(surf, rect)
    return rect

import random


class Wave:
    """Produto final do Builder: uma onda de insetos pronta para ser executada."""

    def __init__(self):
        self.number = 0
        self.spawn_queue: list[str] = []  # nomes dos inimigos, na ordem em que vao nascer
        self.interval = 1.0               # segundos entre um spawn e outro

    @property
    def has_boss(self) -> bool:
        return 'Queen' in self.spawn_queue

    def __str__(self):
        return f'Onda {self.number}: {len(self.spawn_queue)} inimigos a cada {self.interval}s'


class WaveBuilder:
    """Padrao Builder: monta a onda passo a passo.

    wave = WaveBuilder().set_number(3).add_enemy('Crawler', 12).add_enemy('Brute', 3).set_interval(0.8).build()
    """

    def __init__(self):
        self.wave = Wave()
        self.boss: list[str] = []

    def set_number(self, number: int):
        self.wave.number = number
        return self

    def add_enemy(self, name: str, amount: int):
        if name == 'Queen':
            self.boss.extend([name] * amount)  # chefe sempre entra primeiro
        else:
            self.wave.spawn_queue.extend([name] * amount)
        return self

    def set_interval(self, seconds: float):
        self.wave.interval = seconds
        return self

    def build(self) -> Wave:
        random.shuffle(self.wave.spawn_queue)
        self.wave.spawn_queue = self.boss + self.wave.spawn_queue
        return self.wave

# Bug Siege

Jogo 2D top-down de sobrevivência feito em Python com **pygame** para a disciplina
*Linguagem de Programação Aplicada* (UNINTER).

Um soldado está preso numa arena infestada de insetos. Sobreviva a 5 ondas e
derrote a **Rainha da Colmeia** na onda final.

## Controles

| Tecla | Ação |
|---|---|
| W A S D | Mover |
| Mouse | Mirar |
| Clique esquerdo / Espaço | Atirar |
| Shift | Esquiva (fica invulnerável por um instante) |
| ESC | Pausar (na pausa, Q volta ao menu) |

## Regras

- **Vitória:** sobreviver às 5 ondas (a última tem a Rainha, que dispara rajadas e chama filhotes).
- **Derrota:** a vida do soldado chega a zero.
- **Inimigos:** *Crawler* (rápido, zigue-zague), *Brute* (lento e resistente), *Spitter* (mantém distância e cospe ácido).
- Alguns insetos deixam cair **kits médicos** (+25 de vida).
- Pontuação: insetos derrotados + bônus por onda + bônus pela vida restante ao vencer.
  Ao fim da partida você grava suas iniciais no ranking (SQLite).

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Estrutura

```
main.py                 ponto de entrada
core/
  game.py               loop principal: Menu -> Level -> Score
  menu.py               menu com os comandos na tela
  level.py              arena: ondas, HUD, pausa, vitória/derrota
  entity.py             classe abstrata (ABC) de tudo que existe na arena
  player.py enemy.py projectile.py medkit.py
  entity_factory.py     padrão Factory: cria entidades pelo nome
  entity_mediator.py    padrão Mediator: colisões (hitbox manual), dano, pontuação
  wave.py               padrão Builder: monta as ondas
  db_proxy.py           padrão Proxy: acesso ao SQLite
  score.py              tela de fim de jogo e ranking
  const.py              todas as constantes (tamanho da tela, velocidades, vidas...)
  resource.py           caminhos relativos dos assets (funciona no .py e no .exe)
asset/                  imagens e sons
tools/generate_assets.py  gera todos os assets por código (pixel art e sons sintetizados)
tests/                  testes com pytest
```

## Gerar o executável (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name BugSiege main.py
```

Copie a pasta `asset` para dentro de `dist/`, ao lado do `BugSiege.exe`
(os assets não são compilados junto com o exe).

## Assets

Todas as imagens e sons foram gerados por código em `tools/generate_assets.py`
(`python tools/generate_assets.py`), sem arquivos de terceiros.

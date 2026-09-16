from dataclasses import dataclass
from enum import Enum

Posicao = tuple[int, int]


class Lixo(Enum):
    ORGANICO = 1
    RECICLAVEL = 5


class Acao(Enum):
    CIMA = "cima"
    DIREITA = "direita"
    BAIXO = "baixo"
    ESQUERDA = "esquerda"
    PEGAR = "pegar"
    SOLTAR = "soltar"
    NOOP = "noop"


DESLOCAMENTOS = {
    Acao.CIMA: (0, -1), Acao.DIREITA: (1, 0),
    Acao.BAIXO: (0, 1), Acao.ESQUERDA: (-1, 0),
}


@dataclass(frozen=True)
class Celula:
    posicao: Posicao
    lixo: Lixo | None


@dataclass(frozen=True)
class Percepcao:
    posicao: Posicao
    carga: Lixo | None
    lixeira: Posicao
    tamanho: int
    visiveis: tuple[Celula, ...]
    movimentos: tuple[Acao, ...]


def manhattan(a: Posicao, b: Posicao) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def destino(posicao: Posicao, acao: Acao) -> Posicao:
    dx, dy = DESLOCAMENTOS[acao]
    return posicao[0] + dx, posicao[1] + dy


def mover_para(p: Percepcao, alvo: Posicao) -> Acao:
    """Um passo cardinal de menor distância, válido na grade sem obstáculos."""
    if p.posicao == alvo or not p.movimentos:
        return Acao.NOOP
    return min(p.movimentos, key=lambda a: manhattan(destino(p.posicao, a), alvo))
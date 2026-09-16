from math import isfinite
from .objetivos import BaseadoEmObjetivos
from ..tipos import Percepcao, Posicao, manhattan


class BaseadoEmUtilidade(BaseadoEmObjetivos):
    def __init__(self, seed: int = 42, lambda_peso: float = 1.0):
        super().__init__(seed)
        if not isfinite(lambda_peso) or lambda_peso < 0:
            raise ValueError("Lambda deve ser finito e não negativo.")
        self.lambda_peso = lambda_peso

    def utilidade(self, p: Percepcao, pos: Posicao) -> float:
        return (self.mapa[pos].value
                - self.lambda_peso * manhattan(p.posicao, pos)
                - manhattan(pos, p.lixeira))

    def escolher_lixo(self, p: Percepcao) -> Posicao | None:
        lixos = [pos for pos, lixo in self.mapa.items() if lixo is not None]
        # Utilidades negativas continuam elegíveis: há uma tarefa de coleta.
        # A função ordena alvos, não representa o critério de encerramento.
        return min(lixos, key=lambda pos: (-self.utilidade(p, pos),
                   -self.mapa[pos].value, manhattan(p.posicao, pos), pos)) if lixos else None
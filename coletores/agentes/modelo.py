from collections import Counter
from random import Random
from ..tipos import Acao, Percepcao, destino, manhattan, mover_para


class BaseadoEmModelos:
    def __init__(self, seed: int = 42):
        self.visitas = Counter()
        self.carga = None
        self.ultima_posicao = None
        self.sorteio = Random(seed)

    def decidir(self, p: Percepcao) -> Acao:
        # Visitas contam entradas, não o tempo parado ao pegar/soltar lixo.
        if p.posicao != self.ultima_posicao:
            self.visitas[p.posicao] += 1
        self.ultima_posicao, self.carga = p.posicao, p.carga
        if self.carga is not None:
            return Acao.SOLTAR if p.posicao == p.lixeira else mover_para(p, p.lixeira)
        local = next(c for c in p.visiveis if c.posicao == p.posicao)
        if local.lixo is not None:
            return Acao.PEGAR
        lixos = [c for c in p.visiveis if c.lixo is not None]
        if lixos:
            alvo = min(lixos, key=lambda c: (-c.lixo.value,
                       manhattan(p.posicao, c.posicao), c.posicao))
            return mover_para(p, alvo.posicao)
        if not p.movimentos:
            return Acao.NOOP
        menor = min(self.visitas[destino(p.posicao, a)] for a in p.movimentos)
        opcoes = [a for a in p.movimentos
                  if self.visitas[destino(p.posicao, a)] == menor]
        return self.sorteio.choice(opcoes)
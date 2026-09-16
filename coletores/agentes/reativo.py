from random import Random
from ..tipos import Acao, Percepcao, manhattan, mover_para


class ReativoSimples:
    def __init__(self, seed: int = 42):
        # O gerador reproduz a escolha aleatória; não representa memória do mundo.
        self.sorteio = Random(seed)

    def decidir(self, p: Percepcao) -> Acao:
        if p.carga is not None:
            return Acao.SOLTAR if p.posicao == p.lixeira else mover_para(p, p.lixeira)
        local = next(c for c in p.visiveis if c.posicao == p.posicao)
        if local.lixo is not None:
            return Acao.PEGAR
        lixos = [c for c in p.visiveis if c.lixo is not None]
        if lixos:
            alvo = min(lixos, key=lambda c: (-c.lixo.value,
                       manhattan(p.posicao, c.posicao), c.posicao))
            return mover_para(p, alvo.posicao)
        return self.sorteio.choice(p.movimentos) if p.movimentos else Acao.NOOP
from random import Random

from .tipos import Acao, Celula, DESLOCAMENTOS, Lixo, Percepcao, Posicao, destino


def gerar_mapa(seed: int = 42, tamanho: int = 20,
               organicos: int = 10, reciclaveis: int = 5) -> dict[Posicao, Lixo]:
    if tamanho < 2 or min(organicos, reciclaveis) < 0:
        raise ValueError("Tamanho >= 2 e quantidades não negativas são obrigatórios.")
    livres = [(x, y) for y in range(1, tamanho + 1)
              for x in range(1, tamanho + 1)
              if (x, y) not in ((1, 1), (tamanho, tamanho))]
    if organicos + reciclaveis > len(livres):
        raise ValueError("Quantidade de lixos excede as células disponíveis.")
    locais = Random(seed).sample(livres, organicos + reciclaveis)
    tipos = [Lixo.ORGANICO] * organicos + [Lixo.RECICLAVEL] * reciclaveis
    return dict(zip(locais, tipos))


class Ambiente:
    def __init__(self, mapa: dict[Posicao, Lixo], tamanho: int = 20):
        if tamanho < 2:
            raise ValueError("Tamanho mínimo: 2.")
        self.tamanho = tamanho
        self.posicao = (1, 1)
        self.lixeira = (tamanho, tamanho)
        if any(not self.dentro(p) or not isinstance(l, Lixo)
               for p, l in mapa.items()):
            raise ValueError("Mapa contém posição ou lixo inválido.")
        if self.posicao in mapa or self.lixeira in mapa:
            raise ValueError("Início e lixeira devem estar livres.")
        self.lixos = dict(mapa)  # Cópia independente para cada arquitetura.
        self.carga = None
        self.passos = self.movimentos = self.colisoes = self.invalidas = 0
        self.coletados = self.entregues = self.pontos = 0
        self.organicos = self.reciclaveis = 0
        self.historico_entregas: list[str] = []

    def dentro(self, p: Posicao) -> bool:
        return 1 <= p[0] <= self.tamanho and 1 <= p[1] <= self.tamanho

    @property
    def concluido(self) -> bool:
        return not self.lixos and self.carga is None

    def perceber(self) -> Percepcao:
        x, y = self.posicao
        celulas = tuple(
            Celula((i, j), self.lixos.get((i, j)))
            for j in range(y - 1, y + 2) for i in range(x - 1, x + 2)
            if self.dentro((i, j))
        )
        movimentos = tuple(a for a in DESLOCAMENTOS
                           if self.dentro(destino(self.posicao, a)))
        return Percepcao(self.posicao, self.carga, self.lixeira,
                         self.tamanho, celulas, movimentos)

    def executar(self, acao: Acao) -> None:
        if not isinstance(acao, Acao):
            raise ValueError("Ação desconhecida.")
        self.passos += 1  # Um passo é um ciclo com uma ação, inclusive NoOp.
        if acao in DESLOCAMENTOS:
            nova = destino(self.posicao, acao)
            if self.dentro(nova):
                self.posicao = nova
                self.movimentos += 1
            else:
                self.colisoes += 1
        elif acao == Acao.PEGAR:
            if self.carga is None and self.posicao in self.lixos:
                self.carga = self.lixos.pop(self.posicao)
                self.coletados += 1
            else:
                self.invalidas += 1
        elif acao == Acao.SOLTAR:
            if self.carga is not None and self.posicao == self.lixeira:
                self.pontos += self.carga.value
                self.entregues += 1
                self.organicos += self.carga == Lixo.ORGANICO
                self.reciclaveis += self.carga == Lixo.RECICLAVEL
                self.historico_entregas.append(self.carga.name)
                self.carga = None
            else:
                self.invalidas += 1
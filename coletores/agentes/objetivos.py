from collections import Counter, deque
from dataclasses import dataclass

from ..tipos import Acao, DESLOCAMENTOS, Lixo, Percepcao, Posicao, manhattan


@dataclass(frozen=True)
class Intencao:
    tipo: str  # entregar, coletar ou explorar
    alvo: Posicao


def rota_manhattan(inicio: Posicao, fim: Posicao) -> deque[Acao]:
    """Rota mínima na grade livre: primeiro x, depois y; não há diagonais."""
    x, y = inicio
    fx, fy = fim
    rota = deque()
    rota.extend([Acao.DIREITA if fx > x else Acao.ESQUERDA] * abs(fx - x))
    rota.extend([Acao.BAIXO if fy > y else Acao.CIMA] * abs(fy - y))
    return rota


class BaseadoEmObjetivos:
    desejos = ("entregar a carga", "priorizar recicláveis conhecidos",
               "coletar orgânicos", "explorar células desconhecidas")

    def __init__(self, seed: int = 42):
        self.mapa: dict[Posicao, Lixo | None] = {}
        self.visitas = Counter()
        self.posicao = (1, 1)
        self.carga = None
        self.lixeira = (20, 20)
        self.intencao: Intencao | None = None
        self.plano: deque[Acao] = deque()
        self.ultima_posicao = None

    def atualizar_crencas(self, p: Percepcao) -> None:
        self.posicao, self.carga, self.lixeira = p.posicao, p.carga, p.lixeira
        self.mapa.update({c.posicao: c.lixo for c in p.visiveis})
        if p.posicao != self.ultima_posicao:
            self.visitas[p.posicao] += 1
        self.ultima_posicao = p.posicao

    def escolher_lixo(self, p: Percepcao) -> Posicao | None:
        lixos = [pos for pos, lixo in self.mapa.items() if lixo is not None]
        return min(lixos, key=lambda pos: (-self.mapa[pos].value,
                   manhattan(p.posicao, pos), pos)) if lixos else None

    def explorar(self, p: Percepcao) -> Posicao | None:
        # Fronteira = célula já observada ao lado de alguma célula desconhecida.
        def tem_desconhecido(pos):
            for dx, dy in DESLOCAMENTOS.values():
                vizinho = pos[0] + dx, pos[1] + dy
                if (1 <= vizinho[0] <= p.tamanho and 1 <= vizinho[1] <= p.tamanho
                        and vizinho not in self.mapa):
                    return True
            return False
        fronteiras = [pos for pos in self.mapa if tem_desconhecido(pos)]
        return min(fronteiras, key=lambda pos: (manhattan(p.posicao, pos),
                   self.visitas[pos], pos)) if fronteiras else None

    def intencao_valida(self, p: Percepcao) -> bool:
        if self.intencao is None:
            return False
        i = self.intencao
        if i.tipo == "entregar":
            return p.carga is not None
        if p.carga is not None:
            return False
        if i.tipo == "coletar":
            return self.mapa.get(i.alvo) is not None
        # Novos lixos conhecidos interrompem a exploração, não uma coleta em curso.
        return p.posicao != i.alvo and not any(self.mapa.values())

    def deliberar(self, p: Percepcao) -> Intencao | None:
        if p.carga is not None:
            return Intencao("entregar", p.lixeira)
        alvo = self.escolher_lixo(p)
        if alvo is not None:
            return Intencao("coletar", alvo)
        alvo = self.explorar(p)
        return Intencao("explorar", alvo) if alvo is not None else None

    def decidir(self, p: Percepcao) -> Acao:
        self.atualizar_crencas(p)
        if not self.intencao_valida(p):
            self.intencao = self.deliberar(p)
            self.plano = (rota_manhattan(p.posicao, self.intencao.alvo)
                          if self.intencao else deque())
        if self.intencao is None:
            return Acao.NOOP
        if p.posicao == self.intencao.alvo:
            acao = {"entregar": Acao.SOLTAR, "coletar": Acao.PEGAR}.get(
                self.intencao.tipo, Acao.NOOP)
            self.intencao = None
            self.plano.clear()
            return acao
        if not self.plano:
            self.plano = rota_manhattan(p.posicao, self.intencao.alvo)
        return self.plano.popleft()
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Protocol

from .ambiente import Ambiente
from .tipos import Acao, Lixo, Percepcao, Posicao


class Agente(Protocol):
    def decidir(self, p: Percepcao) -> Acao: ...


@dataclass(frozen=True)
class Resultado:
    agente: str
    seed: int
    coletados: int
    entregues: int
    pontos: int
    passos: int
    movimentos: int
    colisoes: int
    invalidas: int
    tempo_ms: float
    concluido: bool
    motivo: str
    organicos: int
    reciclaveis: int
    ordem_entregas: tuple[str, ...]

    def como_dict(self) -> dict:
        return asdict(self)


def simular(nome: str, agente: Agente, mapa: dict[Posicao, Lixo],
            seed: int = 42, max_passos: int = 10000, tamanho: int = 20,
            registrar: bool = False) -> tuple[Resultado, list[dict]]:
    if max_passos < 1:
        raise ValueError("O limite de passos deve ser positivo.")
    ambiente = Ambiente(mapa, tamanho)
    trilha = []
    inicio = perf_counter()
    while not ambiente.concluido and ambiente.passos < max_passos:
        p = ambiente.perceber()
        acao = agente.decidir(p)
        antes = ambiente.posicao
        ambiente.executar(acao)
        if registrar:
            trilha.append({"passo": ambiente.passos, "acao": acao.value,
                           "antes": antes, "posicao": ambiente.posicao,
                           "carga": ambiente.carga.name if ambiente.carga else None,
                           "pontos": ambiente.pontos, "entregues": ambiente.entregues})
    tempo = (perf_counter() - inicio) * 1000
    r = Resultado(nome, seed, ambiente.coletados, ambiente.entregues,
                  ambiente.pontos, ambiente.passos, ambiente.movimentos,
                  ambiente.colisoes, ambiente.invalidas, tempo, ambiente.concluido,
                  "concluido" if ambiente.concluido else "limite_de_passos",
                  ambiente.organicos, ambiente.reciclaveis,
                  tuple(ambiente.historico_entregas))
    return r, trilha
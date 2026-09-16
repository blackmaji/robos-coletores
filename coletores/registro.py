from .agentes.reativo import ReativoSimples
from .agentes.modelo import BaseadoEmModelos

FABRICAS = {
    "reativo": ReativoSimples,
    "modelo": BaseadoEmModelos,
}


def criar_agente(nome: str, seed: int = 42, lambda_peso: float = 1.0):
    return FABRICAS[nome](seed=seed)
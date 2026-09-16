from .agentes.reativo import ReativoSimples
from .agentes.modelo import BaseadoEmModelos
from .agentes.objetivos import BaseadoEmObjetivos
from .agentes.utilidade import BaseadoEmUtilidade

FABRICAS = {
    "reativo": ReativoSimples,
    "modelo": BaseadoEmModelos,
    "bdi": BaseadoEmObjetivos,
    "utilidade": BaseadoEmUtilidade,
}


def criar_agente(nome: str, seed: int = 42, lambda_peso: float = 1.0):
    if nome == "utilidade":
        return FABRICAS[nome](seed=seed, lambda_peso=lambda_peso)
    return FABRICAS[nome](seed=seed)
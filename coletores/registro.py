from .agentes.reativo import ReativoSimples

FABRICAS = {
    "reativo": ReativoSimples,
}


def criar_agente(nome: str, seed: int = 42, lambda_peso: float = 1.0):
    return FABRICAS[nome](seed=seed)
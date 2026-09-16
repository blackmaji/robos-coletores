import unittest
from coletores.ambiente import Ambiente
from coletores.agentes.modelo import BaseadoEmModelos
from coletores.tipos import destino


class TestModelo(unittest.TestCase):
    def test_exploracao_prioriza_destino_nao_visitado(self):
        a = Ambiente({})
        a.posicao = (2, 2)
        agente = BaseadoEmModelos(42)
        agente.visitas.update({(2, 1): 3, (3, 2): 0, (2, 3): 2, (1, 2): 1})
        acao = agente.decidir(a.perceber())
        self.assertEqual(destino(a.posicao, acao), (3, 2))
        self.assertEqual(agente.visitas[(2, 2)], 1)
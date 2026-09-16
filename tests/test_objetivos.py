import unittest
from coletores.ambiente import Ambiente
from coletores.agentes.objetivos import BaseadoEmObjetivos, rota_manhattan
from coletores.simulacao import simular
from coletores.tipos import Lixo, destino, manhattan


class TestObjetivos(unittest.TestCase):
    def test_rota_minima_cardinal(self):
        pos, fim = (3, 7), (18, 2)
        rota = rota_manhattan(pos, fim)
        self.assertEqual(len(rota), manhattan(pos, fim))
        for acao in rota:
            pos = destino(pos, acao)
        self.assertEqual(pos, fim)

    def test_prioridade_e_intencao_persistente(self):
        a = Ambiente({(2, 1): Lixo.ORGANICO, (2, 2): Lixo.RECICLAVEL})
        agente = BaseadoEmObjetivos()
        acao = agente.decidir(a.perceber())
        self.assertEqual(agente.intencao.alvo, (2, 2))
        a.executar(acao)
        agente.decidir(a.perceber())
        self.assertEqual(agente.intencao.alvo, (2, 2))

    def test_exploracao_descobre_lixo_inicialmente_oculto(self):
        r, _ = simular("bdi", BaseadoEmObjetivos(),
                       {(3, 3): Lixo.ORGANICO}, tamanho=4, max_passos=200)
        self.assertTrue(r.concluido)
        self.assertEqual(r.pontos, 1)
import unittest
from coletores.ambiente import Ambiente
from coletores.agentes.reativo import ReativoSimples
from coletores.simulacao import simular
from coletores.tipos import Acao, Lixo


class TestReativo(unittest.TestCase):
    def test_pega_lixo_e_entrega(self):
        r, _ = simular("reativo", ReativoSimples(42),
                       {(2, 1): Lixo.RECICLAVEL}, tamanho=2)
        self.assertTrue(r.concluido)
        self.assertEqual((r.pontos, r.passos, r.movimentos), (5, 4, 2))

    def test_preferencia_local_reciclavel(self):
        a = Ambiente({(2, 1): Lixo.ORGANICO, (1, 2): Lixo.RECICLAVEL})
        self.assertEqual(ReativoSimples().decidir(a.perceber()), Acao.BAIXO)

    def test_limite_nao_declara_conclusao(self):
        r, _ = simular("reativo", ReativoSimples(), {(10, 10): Lixo.ORGANICO},
                       max_passos=1)
        self.assertFalse(r.concluido)
        self.assertEqual(r.motivo, "limite_de_passos")
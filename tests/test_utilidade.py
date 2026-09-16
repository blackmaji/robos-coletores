import unittest
from coletores.ambiente import Ambiente
from coletores.agentes.objetivos import BaseadoEmObjetivos
from coletores.agentes.utilidade import BaseadoEmUtilidade
from coletores.tipos import Lixo


class TestUtilidade(unittest.TestCase):
    def test_custo_pode_superar_prioridade_reciclavel(self):
        a = Ambiente({})
        a.posicao = (19, 20)
        p = a.perceber()
        conhecidos = {(19, 19): Lixo.ORGANICO, (1, 2): Lixo.RECICLAVEL}
        u, b = BaseadoEmUtilidade(), BaseadoEmObjetivos()
        u.mapa.update(conhecidos)
        b.mapa.update(conhecidos)
        self.assertEqual(u.utilidade(p, (19, 19)), -2)
        self.assertEqual(u.utilidade(p, (1, 2)), -68)
        self.assertEqual(u.escolher_lixo(p), (19, 19))
        self.assertEqual(b.escolher_lixo(p), (1, 2))

    def test_lambda_invalido(self):
        for peso in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                BaseadoEmUtilidade(lambda_peso=peso)
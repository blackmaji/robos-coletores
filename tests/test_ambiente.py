import unittest
from collections import Counter

from coletores.ambiente import Ambiente, gerar_mapa
from coletores.tipos import Acao, Lixo


class TestAmbiente(unittest.TestCase):

    def test_mapa_e_semente(self):
        mapa = gerar_mapa(42)

        self.assertEqual(mapa, gerar_mapa(42))
        self.assertEqual(
            Counter(mapa.values()),
            {Lixo.ORGANICO: 10, Lixo.RECICLAVEL: 5},
        )
        self.assertNotIn((1, 1), mapa)
        self.assertNotIn((20, 20), mapa)

    def test_percepcao_nao_revela_mapa_global(self):
        ambiente = Ambiente({
            (2, 2): Lixo.ORGANICO,
            (10, 10): Lixo.RECICLAVEL,
        })

        percepcao = ambiente.perceber()

        self.assertEqual(len(percepcao.visiveis), 4)
        self.assertNotIn(
            (10, 10),
            [celula.posicao for celula in percepcao.visiveis],
        )

        ambiente.posicao = (10, 10)
        self.assertEqual(len(ambiente.perceber().visiveis), 9)

    def test_carga_unitaria_pontuacao_apenas_na_entrega(self):
        ambiente = Ambiente({
            (2, 1): Lixo.RECICLAVEL,
            (1, 2): Lixo.ORGANICO,
        }, tamanho=2)

        ambiente.executar(Acao.CIMA)
        self.assertEqual(ambiente.colisoes, 1)

        ambiente.executar(Acao.DIREITA)
        ambiente.executar(Acao.PEGAR)
        self.assertEqual(ambiente.pontos, 0)

        ambiente.executar(Acao.PEGAR)
        ambiente.executar(Acao.SOLTAR)
        self.assertEqual(ambiente.invalidas, 2)
        self.assertEqual(ambiente.coletados, 1)

        ambiente.executar(Acao.BAIXO)
        ambiente.executar(Acao.SOLTAR)

        self.assertEqual(ambiente.pontos, 5)
        self.assertEqual(ambiente.entregues, 1)
        self.assertIsNone(ambiente.carga)

    def test_execucoes_nao_compartilham_mapa(self):
        mapa = {(2, 1): Lixo.ORGANICO}
        primeiro = Ambiente(mapa)
        segundo = Ambiente(mapa)

        primeiro.executar(Acao.DIREITA)
        primeiro.executar(Acao.PEGAR)

        self.assertEqual(segundo.lixos, mapa)
        self.assertIn((2, 1), mapa)


if __name__ == "__main__":
    unittest.main()
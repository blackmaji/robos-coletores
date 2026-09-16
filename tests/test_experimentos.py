import json
import tempfile
import unittest
from pathlib import Path

from coletores.ambiente import gerar_mapa
from coletores.experimentos import comparar
from coletores.registro import FABRICAS, criar_agente
from coletores.simulacao import simular


class TestExperimentos(unittest.TestCase):
    def test_invariantes_das_quatro_arquiteturas(self):
        for nome in FABRICAS:
            with self.subTest(agente=nome):
                mapa = gerar_mapa(42)
                r, _ = simular(nome, criar_agente(nome), mapa)
                self.assertEqual(len(mapa), 15)
                self.assertEqual(r.pontos, r.organicos + 5 * r.reciclaveis)
                self.assertLessEqual(r.coletados, 15)
                self.assertLessEqual(r.coletados - r.entregues, 1)
                self.assertLessEqual(r.passos, 10000)
                self.assertEqual((r.colisoes, r.invalidas), (0, 0))
                if nome in ("bdi", "utilidade"):
                    self.assertEqual((r.entregues, r.pontos, r.concluido), (15, 35, True))

    def test_exportacao_e_repeticao_controlada(self):
        with tempfile.TemporaryDirectory() as d:
            dados = comparar([42], repeticoes=2, max_passos=50, saida=d)
            self.assertEqual(len(dados["execucoes"]), 8)
            self.assertEqual(len(dados["resumos"]), 4)
            self.assertEqual(len(json.loads((Path(d)/"mapa_seed_42.json").read_text())), 15)
            self.assertTrue((Path(d)/"resumo.csv").is_file())
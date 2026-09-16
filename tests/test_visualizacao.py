import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from coletores.ambiente import gerar_mapa
from coletores.registro import criar_agente
from coletores.simulacao import simular
from coletores.visualizacao import gerar_svg


class TestVisualizacao(unittest.TestCase):
    def test_trilha_animada_coincide_com_estado_final(self):
        mapa = gerar_mapa(42)
        r, trilha = simular("bdi", criar_agente("bdi"), mapa, registrar=True)
        self.assertEqual(len(trilha), r.passos)
        self.assertEqual(trilha[-1]["pontos"], r.pontos)
        self.assertEqual(trilha[-1]["posicao"], (20, 20))
        with tempfile.TemporaryDirectory() as d:
            arquivo = Path(d)/"demo.svg"
            gerar_svg(mapa, trilha, str(arquivo), "Teste & percepção")
            raiz = ET.parse(arquivo).getroot()
            ns = {"s": "http://www.w3.org/2000/svg"}
            anim = raiz.find(".//s:animateTransform", ns)
            self.assertEqual(len(anim.attrib["values"].split(";")), r.passos + 1)
            self.assertEqual(len(raiz.findall(".//s:set", ns)), r.coletados)
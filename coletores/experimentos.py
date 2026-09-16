import csv
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, stdev

from .ambiente import gerar_mapa
from .registro import FABRICAS, criar_agente
from .simulacao import simular


def salvar_csv(arquivo: Path, linhas: list[dict]) -> None:
    with arquivo.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(linhas[0]))
        writer.writeheader()
        writer.writerows(linhas)


def comparar(seeds: list[int], repeticoes: int = 5, max_passos: int = 10000,
             lambda_peso: float = 1.0, saida: str = "saidas/comparacao") -> dict:
    if not seeds or repeticoes < 1 or max_passos < 1:
        raise ValueError("Informe sementes e quantidades positivas.")
    pasta = Path(saida)
    pasta.mkdir(parents=True, exist_ok=True)
    nomes = list(FABRICAS)
    execucoes, resumos = [], []
    for seed in seeds:
        mapa = gerar_mapa(seed)
        mapa_json = [{"x": x, "y": y, "tipo": lixo.name}
                     for (x, y), lixo in sorted(mapa.items())]
        (pasta / f"mapa_seed_{seed}.json").write_text(
            json.dumps(mapa_json, indent=2), encoding="utf-8")
        # Aquecimento fora da amostra de tempo.
        for nome in nomes:
            simular(nome, criar_agente(nome, seed, lambda_peso), mapa,
                    seed, max_passos)
        for repeticao in range(repeticoes):
            # Rotação limita o viés de executar sempre a mesma arquitetura primeiro.
            ordem = nomes[repeticao % len(nomes):] + nomes[:repeticao % len(nomes)]
            for nome in ordem:
                r, _ = simular(nome, criar_agente(nome, seed, lambda_peso), mapa,
                               seed, max_passos)
                execucoes.append({"repeticao": repeticao + 1, **r.como_dict()})
        for nome in nomes:
            linhas = [r for r in execucoes if r["seed"] == seed and r["agente"] == nome]
            primeira = linhas[0]
            # As repetições medem tempo; não são novos mapas independentes.
            for linha in linhas[1:]:
                for campo in ("pontos", "passos", "entregues", "ordem_entregas"):
                    if linha[campo] != primeira[campo]:
                        raise RuntimeError("Trajetória não reprodutível nesta execução.")
            tempos = [r["tempo_ms"] for r in linhas]
            resumos.append({
                "seed": seed, "agente": nome, "coletados": primeira["coletados"],
                "entregues": primeira["entregues"], "pontos": primeira["pontos"],
                "passos": primeira["passos"], "movimentos": primeira["movimentos"],
                "colisoes": primeira["colisoes"], "invalidas": primeira["invalidas"],
                "concluido": primeira["concluido"], "motivo": primeira["motivo"],
                "tempo_mediano_ms": median(tempos), "tempo_medio_ms": mean(tempos),
                "tempo_desvio_ms": stdev(tempos) if len(tempos) > 1 else 0.0,
            })
    dados = {
        "metadados": {"data_utc": datetime.now(timezone.utc).isoformat(),
                      "python": sys.version, "plataforma": platform.platform(),
                      "seeds": seeds, "repeticoes": repeticoes, "max_passos": max_passos,
                      "lambda": lambda_peso, "aquecimentos_por_mapa_agente": 1,
                      "cronometro": "time.perf_counter",
                      "escopo_tempo": "percepcao, decisao e acao; sem geracao, I/O ou desenho",
                      "passo": "uma acao, incluindo pegar, soltar e noop",
                      "pontuacao": "apenas lixo entregue na lixeira"},
        "resumos": resumos, "execucoes": execucoes,
    }
    (pasta / "resultados.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    salvar_csv(pasta / "execucoes.csv", execucoes)
    salvar_csv(pasta / "resumo.csv", resumos)
    return dados
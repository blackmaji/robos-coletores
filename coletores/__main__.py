import argparse
import json
from math import isfinite
from pathlib import Path

from .ambiente import gerar_mapa
from .registro import FABRICAS, criar_agente
from .simulacao import simular
from .tipos import Lixo


def positivo(texto):
    valor = int(texto)
    if valor < 1:
        raise argparse.ArgumentTypeError("Informe um inteiro positivo.")
    return valor


def peso_valido(texto):
    valor = float(texto)
    if not isfinite(valor) or valor < 0:
        raise argparse.ArgumentTypeError("Informe um número finito não negativo.")
    return valor


def main():
    parser = argparse.ArgumentParser(description="Robôs coletores em matriz 20x20")
    comandos = parser.add_subparsers(dest="comando", required=True)
    executar = comandos.add_parser("simular", help="Executa um agente")
    executar.add_argument("--agente", choices=list(FABRICAS), default="bdi")
    executar.add_argument("--seed", type=int, default=42)
    executar.add_argument("--mapa", help="JSON com lista de x, y e tipo; substitui o mapa gerado")
    executar.add_argument("--svg", help="Arquivo SVG animado para abrir no navegador")
    executar.add_argument("--duracao", type=positivo, default=35)
    comparar_parser = comandos.add_parser("comparar", help="Compara as quatro arquiteturas")
    comparar_parser.add_argument("--seeds", type=int, nargs="+", default=[42])
    comparar_parser.add_argument("--repeticoes", type=positivo, default=5)
    comparar_parser.add_argument("--saida", default="saidas/comparacao")
    for sub in (executar, comparar_parser):
        sub.add_argument("--max-passos", type=positivo, default=10000)
        sub.add_argument("--lambda-peso", type=peso_valido, default=1.0)
    args = parser.parse_args()
    if args.comando == "comparar":
        from .experimentos import comparar
        dados = comparar(args.seeds, args.repeticoes, args.max_passos,
                         args.lambda_peso, args.saida)
        for r in dados["resumos"]:
            print(f'Seed {r["seed"]} | {r["agente"]}: {r["entregues"]}/15 entregues, '
                  f'{r["pontos"]}/35 pontos, {r["passos"]} ações, '
                  f'{r["tempo_mediano_ms"]:.3f} ms, {r["motivo"]}')
        print(f"Resultados gravados em {Path(args.saida).resolve()}")
        return
    mapa = gerar_mapa(args.seed)
    if args.mapa:
        itens = json.loads(Path(args.mapa).read_text(encoding="utf-8"))
        mapa = {(i["x"], i["y"]): Lixo[i["tipo"]] for i in itens}
        if len(mapa) != len(itens):
            parser.error("O mapa contém posições duplicadas.")
    r, _ = simular(args.agente, criar_agente(args.agente, args.seed, args.lambda_peso),
                   mapa, args.seed, args.max_passos)
    print(json.dumps(r.como_dict(), ensure_ascii=False, indent=2))
    if args.svg:
        from .visualizacao import gerar_svg
        # Uma segunda execução gera a trilha sem contaminar o tempo exibido acima.
        _, trilha = simular(args.agente,
                            criar_agente(args.agente, args.seed, args.lambda_peso),
                            mapa, args.seed, args.max_passos, registrar=True)
        gerar_svg(mapa, trilha, args.svg, f"Agente {args.agente} | seed {args.seed}", args.duracao)
        print(f"Animação: {Path(args.svg).resolve()}")


if __name__ == "__main__":
    main()
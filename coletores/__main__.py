import argparse
import json
from math import isfinite
from .ambiente import gerar_mapa
from .registro import FABRICAS, criar_agente
from .simulacao import simular


def main():
    p = argparse.ArgumentParser(description="Robôs coletores 20x20")
    comandos = p.add_subparsers(dest="comando", required=True)
    s = comandos.add_parser("simular")
    s.add_argument("--agente", choices=list(FABRICAS), default="reativo")
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--max-passos", type=int, default=10000)
    s.add_argument("--lambda-peso", type=float, default=1.0)
    args = p.parse_args()
    if args.max_passos < 1 or not isfinite(args.lambda_peso) or args.lambda_peso < 0:
        p.error("Limite positivo e lambda finito não negativo são obrigatórios.")
    agente = criar_agente(args.agente, args.seed, args.lambda_peso)
    r, _ = simular(args.agente, agente, gerar_mapa(args.seed),
                   args.seed, args.max_passos)
    print(json.dumps(r.como_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
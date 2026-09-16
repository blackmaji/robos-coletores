from html import escape
from pathlib import Path

from .tipos import Lixo, Posicao


def gerar_svg(mapa: dict[Posicao, Lixo], trilha: list[dict], arquivo: str,
              titulo: str = "Robôs coletores de lixo", duracao: float = 35) -> None:
    if duracao <= 0:
        raise ValueError("A duração deve ser positiva.")
    celula, margem = 27, 55
    def centro(p):
        return margem + (p[0] - 0.5) * celula, 95 + (p[1] - 0.5) * celula
    elementos = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="755" viewBox="0 0 760 755">',
        f'<title>{escape(titulo)}</title>',
        '<desc>Mapa completo para o observador. O agente usa apenas os sensores locais.</desc>',
        '<rect width="760" height="755" fill="#f6f8fb"/>',
        f'<text x="30" y="35" font-size="23" font-family="sans-serif" fill="#172b4d">{escape(titulo)}</text>',
        '<text x="30" y="62" font-size="14" font-family="sans-serif">Visão do observador | O orgânico +1 | R reciclável +5 | X lixeira</text>',
    ]
    for i in range(21):
        elementos.extend([
            f'<path d="M {margem+i*celula} 95 V 635" stroke="#d3dbe6"/>',
            f'<path d="M {margem} {95+i*celula} H 595" stroke="#d3dbe6"/>',
        ])
        if i < 20:
            elementos.extend([
                f'<text x="{margem+(i+.5)*celula}" y="85" text-anchor="middle" font-size="10" font-family="sans-serif">{i+1}</text>',
                f'<text x="40" y="{95+(i+.65)*celula}" text-anchor="middle" font-size="10" font-family="sans-serif">{i+1}</text>',
            ])
    n = max(len(trilha), 1)
    coletas = {tuple(e["posicao"]): e["passo"] for e in trilha if e["acao"] == "pegar"}
    for pos, lixo in mapa.items():
        x, y = centro(pos)
        cor = "#147d64" if lixo == Lixo.RECICLAVEL else "#a26929"
        letra = "R" if lixo == Lixo.RECICLAVEL else "O"
        elementos.append(f'<g><circle cx="{x}" cy="{y}" r="10" fill="{cor}"/>')
        elementos.append(f'<text x="{x}" y="{y+4}" text-anchor="middle" fill="white" font-size="12" font-family="sans-serif">{letra}</text>')
        if pos in coletas:
            elementos.append(f'<set attributeName="visibility" to="hidden" begin="{coletas[pos]/n*duracao:.6f}s" fill="freeze"/>')
        elementos.append('</g>')
    x, y = centro((20, 20))
    elementos.append(f'<rect x="{x-12}" y="{y-12}" width="24" height="24" rx="4" fill="#172b4d"/>')
    elementos.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" fill="white" font-size="16" font-family="sans-serif">X</text>')
    valores = ";".join(f"{centro(p)[0]},{centro(p)[1]}" for p in
                       [(1, 1)] + [tuple(e["posicao"]) for e in trilha])
    tempos = ";".join(f"{i/n:.8f}" for i in range(n + 1))
    x0, y0 = centro((1, 1))
    elementos.append(f'<g transform="translate({x0},{y0})"><circle r="12" fill="#3267e3" stroke="white" stroke-width="2"/>')
    elementos.append('<text y="4" text-anchor="middle" fill="white" font-size="11" font-family="sans-serif">A</text>')
    if trilha:
        elementos.append(f'<animateTransform attributeName="transform" type="translate" values="{valores}" keyTimes="{tempos}" calcMode="discrete" dur="{duracao}s" fill="freeze"/>')
    elementos.append('</g>')
    fim = trilha[-1] if trilha else {"passo": 0, "pontos": 0, "entregues": 0}
    elementos.extend([
        '<text x="30" y="674" font-size="15" font-family="sans-serif">Reprodução automática. Recarregue o arquivo no navegador para reiniciar.</text>',
        f'<text x="30" y="701" font-size="15" font-family="sans-serif">Resultado final: {fim["entregues"]}/15 entregues | {fim["pontos"]}/35 pontos | {fim["passo"]} ações</text>',
        '<text x="30" y="727" font-size="12" font-family="sans-serif">A animação é acelerada e não representa o tempo de processamento medido.</text>',
        '</svg>',
    ])
    caminho = Path(arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(elementos), encoding="utf-8")
#!/usr/bin/env python3
"""Gera os gráficos estáticos (SVG) da documentação a partir de data/resultados/exemplos-calculados.json.

Os gráficos ilustram resultados calculados sobre dados SINTÉTICOS. As tabelas equivalentes estão em
docs/anexos/exemplos-calculados.md (versão em tabela de cada gráfico).

Uso:
    python src/gerar_graficos.py
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data" / "resultados" / "exemplos-calculados.json"
SAIDA = RAIZ / "assets" / "graficos"

# Paleta de referência validada (categórica, rampa azul, status e tinta) — ver docs/ux-identidade-visual.md
SUP, PLANO = "#fcfcfb", "#f9f9f7"
TINTA, TINTA2, MUDO = "#0b0b0b", "#52514e", "#6f6e69"
GRADE, EIXO = "#e1e0d9", "#c3c2b7"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
AZUL = {250: "#86b6ef", 300: "#6da7ec", 400: "#3987e5", 450: "#2a78d6", 550: "#1c5cab", 700: "#0d366b"}
BOM, ATENCAO, SERIO, CRITICO = "#0ca30c", "#fab219", "#ec835a", "#d03b3b"
FONTE = "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
MESES = ["jul/25", "ago/25", "set/25", "out/25", "nov/25", "dez/25", "jan/26", "fev/26", "mar/26", "abr/26",
         "mai/26", "jun/26"]


def mil(v: float, casas: int = 1) -> str:
    s = f"{abs(v) / 1000:.{casas}f}".replace(".", ",")
    sinal = "-" if v < 0 else ""
    return f"{sinal}R$ {s} mil"


def brl0(v: float) -> str:
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def t(x, y, texto, tam=12, cor=TINTA2, peso=400, ancora="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONTE}" font-size="{tam}" fill="{cor}" '
            f'font-weight="{peso}" text-anchor="{ancora}" {extra}>{escape(texto)}</text>')


def svg(larg, alt, corpo, titulo, descricao):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{larg}" height="{alt}" viewBox="0 0 {larg} {alt}" '
            f'role="img" aria-labelledby="t d">\n<title id="t">{escape(titulo)}</title>\n'
            f'<desc id="d">{escape(descricao)}</desc>\n'
            f'<rect width="{larg}" height="{alt}" fill="{SUP}"/>\n{corpo}\n</svg>\n')


def barra_h(x0, x1, y, alt, cor, raio=4):
    """Barra horizontal com ponta de dado arredondada e base (zero) reta."""
    esq, dir_ = min(x0, x1), max(x0, x1)
    w = max(dir_ - esq, 0.5)
    r = min(raio, w / 2, alt / 2)
    if x1 >= x0:  # cresce para a direita: ponta arredondada à direita
        d = (f"M{esq},{y} H{dir_ - r} Q{dir_},{y} {dir_},{y + r} V{y + alt - r} Q{dir_},{y + alt} {dir_ - r},{y + alt} "
             f"H{esq} Z")
    else:
        d = (f"M{dir_},{y} H{esq + r} Q{esq},{y} {esq},{y + r} V{y + alt - r} Q{esq},{y + alt} {esq + r},{y + alt} "
             f"H{dir_} Z")
    return f'<path d="{d}" fill="{cor}"/>'


def cabecalho(titulo, subtitulo, larg):
    return t(24, 32, titulo, 16, TINTA, 600) + "\n" + t(24, 52, subtitulo, 12, TINTA2)


# --------------------------------------------------------------------------- 1. estimativa progressiva
def grafico_estimativa(R):
    est = R["estimativa_EMP-A"]
    real = est["valor_real_brl"]
    niveis = est["niveis"]
    L, A = 960, 400
    x0, x1 = 250, 730
    lo, hi = 110_000, 160_000
    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    topo, passo = 112, 64
    c = [cabecalho("Estimativa progressiva do custo total da EMP-A (fictícia), out/2025 a mar/2026",
                   "Faixa P10 a P90 de 20.000 simulações; ponto = P50; linha vertical = valor real do gabarito. "
                   "Dados sintéticos.", L)]
    for v in range(lo, hi + 1, 10_000):
        c.append(f'<line x1="{X(v):.1f}" y1="{topo - 24}" x2="{X(v):.1f}" y2="{topo + 4 * passo - 16}" '
                 f'stroke="{GRADE}" stroke-width="1"/>')
        c.append(t(X(v), topo + 4 * passo, f"R$ {v // 1000} mil", 11, MUDO, ancora="middle"))
    rotulos = {"0": ("N0", "composição da frota"), "1": ("N1", "+ duas respostas"),
               "2": ("N2", "+ extratos e 3 meses de notas"), "3": ("N3", "+ apólice, IPVA e multas")}
    for i, k in enumerate(["0", "1", "2", "3"]):
        n = niveis[k]
        y = topo + i * passo
        c.append(t(24, y + 4, rotulos[k][0], 13, TINTA, 600))
        c.append(t(56, y + 4, rotulos[k][1], 12, TINTA2))
        c.append(t(56, y + 20, f"{round(100 * n['parcela_observada'])}% observado", 11, MUDO))
        c.append(barra_h(X(n["p10"]), X(n["p90"]), y - 7, 14, AZUL[300]))
        # ponta esquerda também é dado: arredondar os dois lados
        c.append(f'<circle cx="{X(n["p50"]):.1f}" cy="{y}" r="6" fill="{AZUL[550]}" stroke="{SUP}" stroke-width="2"/>')
        c.append(t(X(n["p10"]) - 8, y + 4, mil(n["p10"]), 11, TINTA2, ancora="end"))
        c.append(t(X(n["p90"]) + 8, y + 4, mil(n["p90"]), 11, TINTA2))
        ok = n["contem_valor_real"]
        cor = BOM if ok else SERIO
        icone = ("M-4,0 L-1,3 L4,-3" if ok else "M0,-4 V1 M0,3.5 V4")
        c.append(f'<g transform="translate({x1 + 96},{y})"><circle r="7" fill="none" stroke="{cor}" stroke-width="1.5"/>'
                 f'<path d="{icone}" stroke="{cor}" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>')
        c.append(t(x1 + 110, y + 4, "contém o real" if ok else "não contém o real", 12, TINTA2))
    xr = X(real)
    c.append(f'<line x1="{xr:.1f}" y1="{topo - 30}" x2="{xr:.1f}" y2="{topo + 3 * passo + 16}" stroke="{TINTA}" '
             f'stroke-width="1.5"/>')
    c.append(t(xr, topo - 36, f"valor real {brl0(real)}", 11, TINTA, 600, "middle"))
    return svg(L, A, "\n".join(c), "Estimativa progressiva da EMP-A",
               "Faixas P10 a P90 por nível de informação N0 a N3, com P50 e valor real. A faixa estreita a cada nível; "
               "no N3 o valor real fica acima do P90.")


# --------------------------------------------------------------------------- 2. decomposição LMDI
def grafico_lmdi(R):
    casos = [("pares_C-V01", "C-V01 contra os pares", "jan a jun/2026; mediana de 27 cavalos"),
             ("pares_C-V03", "C-V03 contra os pares", "jan a jun/2026; mediana de 27 cavalos"),
             ("temporal_C-V07", "C-V07 contra o próprio histórico", "jan-jun/2026 contra jul-dez/2025")]
    itens = [("atividade", "Atividade (km)", S1), ("intensidade", "Intensidade (L/km)", S2),
             ("preco", "Preço (R$/L)", S3), ("diferenca", "Diferença total", TINTA2)]
    L, A = 960, 600
    xa, xb, lo, hi = 330, 880, -60_000, 90_000
    def X(v):
        return xa + (v - lo) / (hi - lo) * (xb - xa)
    c = [cabecalho("Decomposição do custo de combustível em atividade, intensidade e preço (LMDI)",
                   "Os três efeitos somam exatamente a diferença. EMP-C, dados sintéticos.", L)]
    lx = 24
    for _, nome, cor in itens:
        c.append(f'<rect x="{lx}" y="68" width="12" height="12" rx="2" fill="{cor}"/>')
        c.append(t(lx + 18, 78, nome, 12, TINTA2))
        lx += 18 + len(nome) * 6.6 + 24
    topo = 112
    alt_painel = 156
    base_eixo = topo + 3 * alt_painel - 8
    for v in range(lo, hi + 1, 30_000):
        c.append(f'<line x1="{X(v):.1f}" y1="{topo}" x2="{X(v):.1f}" y2="{base_eixo}" '
                 f'stroke="{EIXO if v == 0 else GRADE}" stroke-width="1"/>')
        c.append(t(X(v), base_eixo + 16, (f"{'+' if v > 0 else ''}{v // 1000} mil" if v else "0"), 10, MUDO,
                   ancora="middle"))
    for j, (chave, titulo, sub) in enumerate(casos):
        r = R["lmdi"][chave]
        y0 = topo + j * alt_painel
        c.append(t(24, y0 + 14, titulo, 13, TINTA, 600))
        c.append(t(24, y0 + 30, sub, 11, MUDO))
        for i, (k, nome, cor) in enumerate(itens):
            v = r[k]
            y = y0 + 40 + i * 26
            c.append(t(48, y + 11, nome, 12, TINTA2))
            c.append(barra_h(X(0), X(v), y, 14, cor))
            rot = ("+" if v > 0 else "") + mil(v)
            if v >= 0:
                c.append(t(X(v) + 6, y + 11, rot, 11, TINTA2))
            else:
                c.append(t(X(v) - 6, y + 11, rot, 11, TINTA2, ancora="end"))
    return svg(L, A, "\n".join(c), "Decomposição LMDI do custo de combustível",
               "Para três veículos da EMP-C, a diferença de custo é separada em efeito atividade, intensidade e preço. "
               "C-V01 custa mais por rodar mais; C-V03 paga mais caro e consome mais; C-V07 piorou o consumo.")


# --------------------------------------------------------------------------- 3. CUSUM
def grafico_cusum(R):
    s7 = R["consumo_EMP-C"]["series"]["C-V07"]
    s5 = R["consumo_EMP-C"]["series"]["C-V05"]
    h = R["consumo_EMP-C"]["cusum_h"]
    alarme = R["consumo_EMP-C"]["alarmes"]["C-V07"]
    meses = list(s7["razao_pares"].keys())
    L, A = 960, 500
    x0, x1 = 90, 820
    def X(i):
        return x0 + i * (x1 - x0) / (len(meses) - 1)
    c = [cabecalho("C-V07: rendimento em relação aos pares e soma acumulada de desvios (CUSUM)",
                   "Razão = km/L do veículo ÷ mediana dos pares no mês. Cinza: C-V05, veículo sem desvio. "
                   "EMP-C, dados sintéticos.", L)]
    # painel 1
    t1, h1, lo1, hi1 = 92, 170, 0.75, 1.05
    def Y1(v):
        return t1 + (hi1 - v) / (hi1 - lo1) * h1
    for v in (0.8, 0.9, 1.0):
        c.append(f'<line x1="{x0}" y1="{Y1(v):.1f}" x2="{x1}" y2="{Y1(v):.1f}" stroke="{EIXO if v == 1.0 else GRADE}" '
                 f'stroke-width="1"/>')
        c.append(t(x0 - 10, Y1(v) + 4, f"{v:.1f}".replace(".", ","), 11, MUDO, ancora="end"))
    i_jan = meses.index("2026-01")
    c.append(f'<line x1="{X(i_jan) - (X(1) - X(0)) / 2:.1f}" y1="{t1}" x2="{X(i_jan) - (X(1) - X(0)) / 2:.1f}" '
             f'y2="{t1 + h1}" stroke="{GRADE}" stroke-width="1"/>')
    c.append(t(X(i_jan) - (X(1) - X(0)) / 2 + 6, t1 + 12, "início da queda", 11, MUDO))
    for serie, cor, larg_ in ((s5, EIXO, 2), (s7, S1, 2)):
        pts = " ".join(f"{X(i):.1f},{Y1(serie['razao_pares'][m]):.1f}" for i, m in enumerate(meses))
        c.append(f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="{larg_}" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
    c.append(f'<circle cx="{X(len(meses) - 1):.1f}" cy="{Y1(s7["razao_pares"][meses[-1]]):.1f}" r="4.5" fill="{S1}" '
             f'stroke="{SUP}" stroke-width="2"/>')
    c.append(t(x1 + 10, Y1(s7["razao_pares"][meses[-1]]) + 4, "C-V07", 12, TINTA, 600))
    c.append(t(x1 + 10, Y1(s5["razao_pares"][meses[-1]]) + 4, "C-V05", 12, TINTA2))
    # painel 2
    t2, h2, hi2 = 320, 130, 22
    def Y2(v):
        return t2 + (hi2 - v) / hi2 * h2
    c.append(t(x0, t2 - 14, "CUSUM de C-V07 (unidades de desvio-padrão intraveículo)", 12, TINTA2, 600))
    for v in (0, 10, 20):
        c.append(f'<line x1="{x0}" y1="{Y2(v):.1f}" x2="{x1}" y2="{Y2(v):.1f}" stroke="{EIXO if v == 0 else GRADE}" '
                 f'stroke-width="1"/>')
        c.append(t(x0 - 10, Y2(v) + 4, str(v), 11, MUDO, ancora="end"))
    c.append(f'<line x1="{x0}" y1="{Y2(h):.1f}" x2="{x1}" y2="{Y2(h):.1f}" stroke="{TINTA2}" stroke-width="1.5"/>')
    c.append(t(x1 + 10, Y2(h) + 4, f"limiar h = {h:g}", 11, TINTA2))
    pts = " ".join(f"{X(i):.1f},{Y2(s7['cusum'][m]):.1f}" for i, m in enumerate(meses))
    c.append(f'<polyline points="{pts}" fill="none" stroke="{S1}" stroke-width="2" stroke-linejoin="round" '
             f'stroke-linecap="round"/>')
    ia = meses.index(alarme)
    c.append(f'<circle cx="{X(ia):.1f}" cy="{Y2(s7["cusum"][alarme]):.1f}" r="5" fill="{SERIO}" stroke="{SUP}" '
             f'stroke-width="2"/>')
    c.append(t(X(ia) + 10, Y2(s7["cusum"][alarme]) - 8, f"alarme em {MESES[ia]}", 12, TINTA, 600))
    for i, m in enumerate(MESES):
        c.append(t(X(i), t2 + h2 + 22, m, 10, MUDO, ancora="middle"))
    return svg(L, A, "\n".join(c), "Rendimento relativo e CUSUM de C-V07",
               "A razão entre o rendimento de C-V07 e a mediana dos pares cai de cerca de 0,95 para 0,81 a partir de "
               "janeiro de 2026; o CUSUM passa do limiar 5 em fevereiro de 2026.")


# --------------------------------------------------------------------------- 4. caixa x competência
def grafico_caixa(R):
    cx = R["caixa_vs_competencia_EMP-B"]
    meses = list(cx["caixa"].keys())
    L, A = 960, 400
    x0, x1, t0, h0, hi = 90, 800, 96, 230, 400_000
    def X(i):
        return x0 + i * (x1 - x0) / (len(meses) - 1)
    def Y(v):
        return t0 + (hi - v) / hi * h0
    c = [cabecalho("Custo mensal da EMP-B (fictícia): caixa e competência",
                   "Competência distribui seguro e IPVA pelos meses de vigência; caixa registra a data do pagamento.", L)]
    c.append(f'<rect x="24" y="66" width="12" height="3" rx="1.5" fill="{S1}"/>' + t(42, 71, "Competência", 12, TINTA2))
    c.append(f'<rect x="140" y="66" width="12" height="3" rx="1.5" fill="{S2}"/>' + t(158, 71, "Caixa", 12, TINTA2))
    for v in range(0, hi + 1, 100_000):
        c.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{EIXO if v == 0 else GRADE}" '
                 f'stroke-width="1"/>')
        c.append(t(x0 - 10, Y(v) + 4, f"R$ {v // 1000} mil" if v else "0", 11, MUDO, ancora="end"))
    for serie, cor in (("caixa", S2), ("competencia", S1)):
        pts = " ".join(f"{X(i):.1f},{Y(cx[serie][m]):.1f}" for i, m in enumerate(meses))
        c.append(f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="2" stroke-linejoin="round" '
                 f'stroke-linecap="round"/>')
        c.append(f'<circle cx="{X(len(meses) - 1):.1f}" cy="{Y(cx[serie][meses[-1]]):.1f}" r="4.5" fill="{cor}" '
                 f'stroke="{SUP}" stroke-width="2"/>')
    ia = meses.index("2026-04")
    c.append(f'<circle cx="{X(ia):.1f}" cy="{Y(cx["caixa"]["2026-04"]):.1f}" r="4.5" fill="{S2}" stroke="{SUP}" '
             f'stroke-width="2"/>')
    c.append(t(X(ia) + 10, Y(cx["caixa"]["2026-04"]) - 2, f"abr/26: {mil(cx['caixa']['2026-04'])} no caixa", 12,
               TINTA, 600))
    c.append(t(X(ia) + 10, Y(cx["caixa"]["2026-04"]) + 14, "renovação anual do seguro paga à vista", 11, TINTA2))
    c.append(t(x1 + 10, Y(cx["competencia"][meses[-1]]) - 6, "Competência", 12, TINTA2))
    c.append(t(x1 + 10, Y(cx["caixa"][meses[-1]]) + 14, "Caixa", 12, TINTA2))
    for i, m in enumerate(MESES):
        c.append(t(X(i), t0 + h0 + 22, m, 10, MUDO, ancora="middle"))
    return svg(L, A, "\n".join(c), "Caixa e competência da EMP-B",
               "As duas séries ficam próximas, exceto em abril de 2026, quando o caixa sobe para cerca de "
               "R$ 370 mil pela renovação do seguro paga à vista, enquanto a competência fica em cerca de R$ 182 mil.")


# --------------------------------------------------------------------------- 5. cenários
def grafico_cenarios(R):
    cen = R["oportunidades"]["EMP-C"]["cenarios"]
    nomes = [("conservador", "Conservador", "só oportunidades validadas"),
             ("base", "Base", "+ anomalias com evidência"),
             ("otimista", "Otimista", "+ hipóteses a validar")]
    cores = [AZUL[250], AZUL[400], AZUL[550]]
    L, A = 960, 380
    x0, x1, t0, h0, hi = 90, 900, 96, 200, 300_000
    def Y(v):
        return t0 + (hi - v) / hi * h0
    c = [cabecalho("Economia líquida anual estimada por cenário, EMP-C (fictícia)",
                   "Escada de evidência; inclui custos de ação e de operar o plano. Hipóteses de simulação, não "
                   "promessa de economia.", L)]
    for v in range(0, hi + 1, 100_000):
        c.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{EIXO if v == 0 else GRADE}" '
                 f'stroke-width="1"/>')
        c.append(t(x0 - 10, Y(v) + 4, f"R$ {v // 1000} mil" if v else "0", 11, MUDO, ancora="end"))
    w = 24
    for i, ((k, nome, sub), cor) in enumerate(zip(nomes, cores)):
        cx_ = x0 + (i + 0.5) * (x1 - x0) / 3
        v = cen[k]["economia_liquida_anual"]
        ytop = Y(v)
        r = 4
        d = (f"M{cx_ - w / 2},{Y(0)} V{ytop + r} Q{cx_ - w / 2},{ytop} {cx_ - w / 2 + r},{ytop} H{cx_ + w / 2 - r} "
             f"Q{cx_ + w / 2},{ytop} {cx_ + w / 2},{ytop + r} V{Y(0)} Z")
        c.append(f'<path d="{d}" fill="{cor}"/>')
        c.append(t(cx_, ytop - 10, mil(v), 13, TINTA, 600, "middle"))
        c.append(t(cx_, Y(0) + 22, nome, 12, TINTA, 600, "middle"))
        c.append(t(cx_, Y(0) + 38, sub, 11, TINTA2, ancora="middle"))
        pb = cen[k]["payback_meses"]
        c.append(t(cx_, Y(0) + 54, f"payback {pb:.1f} mês".replace(".", ",") if pb else "", 11, MUDO,
                   ancora="middle"))
    return svg(L, A, "\n".join(c), "Cenários de economia da EMP-C",
               "Economia líquida anual estimada: conservador cerca de R$ 21 mil, base cerca de R$ 120 mil e "
               "otimista cerca de R$ 257 mil.")


def main():
    R = json.loads(ENTRADA.read_text(encoding="utf-8"))
    SAIDA.mkdir(parents=True, exist_ok=True)
    arquivos = {
        "estimativa-progressiva.svg": grafico_estimativa(R),
        "decomposicao-lmdi.svg": grafico_lmdi(R),
        "cusum-c-v07.svg": grafico_cusum(R),
        "caixa-competencia.svg": grafico_caixa(R),
        "cenarios-economia.svg": grafico_cenarios(R),
    }
    for nome, conteudo in arquivos.items():
        (SAIDA / nome).write_text(conteudo, encoding="utf-8")
    print("ok:", ", ".join(arquivos))


if __name__ == "__main__":
    main()

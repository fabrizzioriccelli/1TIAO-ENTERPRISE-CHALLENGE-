#!/usr/bin/env python3
"""Gera a animação do vídeo da Sprint 1, sincronizada com o texto do roteiro.

O texto da narração é lido de docs/video/narracao.md (tabela de cenas e frases). O tempo de cada cena e de cada frase sai da
contagem de palavras, a 140 palavras por minuto, com uma pausa no fim de cada bloco. Os números da tela vêm de
data/resultados/exemplos-calculados.json.

Saídas:
  assets/fontes/video.html     página animada; a função render(t) desenha o instante t (em segundos)
  docs/video/narracao.md       texto para o narrador, com o tempo de início de cada frase
  docs/video/legendas.srt      legendas no formato SRT, para o YouTube (opcional)

O vídeo em si é gravado quadro a quadro por src/gravar_video.js (requer Node.js, puppeteer e ffmpeg).
O vídeo não tem voz: o enunciado exige narração humana, gravada por um integrante sobre a animação.

Uso:
    python src/gerar_video.py
"""
from __future__ import annotations

import json
import re

from gerar_visuais import ICONE, PULSO, R, RAIZ, SAIDA, dec, mil

PPM = 140          # ritmo da narração, em palavras por minuto
PAUSA_BLOCO = 1.5  # segundos de respiro no fim de cada bloco
ENTRADA = 0.6      # segundos entre o início da cena e a primeira frase
PRE = 3.0          # contagem regressiva antes da primeira fala
FIM = 2.5          # tela final depois da última fala
REPO = "github.com/fabrizzioriccelli/1TIAO-ENTERPRISE-CHALLENGE-"
INTEGRANTES = ["Bruna Collavite", "Fabio Guntovitch", "Fabrizzio Riccelli", "Gabriel Tamais", "Natasha Zonta"]


def blocos_do_roteiro() -> list[dict]:
    texto = (RAIZ / "docs" / "video" / "narracao.md").read_text(encoding="utf-8")
    saida = []
    for linha in texto.splitlines():
        cena = re.match(r"^\| \*\*[\d:]+\*\* \| \*\*Cena (\d+): (.+?)\*\* \|$", linha)
        frase = re.match(r"^\| [\d:]+ \| (.+) \|$", linha)
        if cena:
            saida.append({"n": int(cena.group(1)), "titulo": cena.group(2), "frases": []})
        elif frase and saida:
            saida[-1]["frases"].append(frase.group(1).replace("\\|", "|"))
    return saida


def cronometrar(blocos: list[dict]) -> float:
    t = PRE
    for b in blocos:
        b["ini"] = t
        tf = t + ENTRADA
        b["cues"] = []
        for f in b["frases"]:
            dur = len(f.split()) / PPM * 60
            b["cues"].append({"ini": round(tf, 2), "fim": round(tf + dur, 2), "texto": f})
            tf += dur
        b["fim"] = round(tf + PAUSA_BLOCO, 2)
        t = b["fim"]
    return t + FIM


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def srt_tempo(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


# ---------------------------------------------------------------- elementos animados
# data-a: tipo de animação; data-c: índice da frase (cue) dentro do bloco; data-dl: atraso em segundos;
# data-d: duração em segundos.

def an(tipo: str, cue: int = 0, atraso: float = 0.0, dur: float = 0.7) -> str:
    return f'data-a="{tipo}" data-c="{cue}" data-dl="{atraso}" data-d="{dur}"'


def contador(valor: float, fmt: str, cue: int = 0, atraso: float = 0.0, dur: float = 1.4, de: float = 0) -> str:
    return (f'<span {an("count", cue, atraso, dur)} data-de="{de}" data-ate="{valor}" data-fmt="{fmt}">'
            f'{valor}</span>')


def cena_abertura():
    pills = "".join(f'<span class="pill" {an("up", 2, 0.9 + i * 1.1)}>{t}</span>' for i, t in
                    enumerate(["O que construir", "Com quais dados", "Como provar que funciona"]))
    return f"""
<div class="abertura">
  <svg class="pulso-grande" viewBox="0 0 1500 220" aria-hidden="true">
    <path pathLength="1" {an("draw", 0, 0, 2.2)} d="M0 150 H520 L585 40 L650 200 L715 95 H1500" fill="none"
      stroke="#2a78d6" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>
  <div class="marca enorme" {an("up", 0, 0.8)}>{PULSO.format(w=78, h=46, cor="#2a78d6")}<span>frota <b>pulse</b></span></div>
  <h1 {an("up", 1, 0)}>Calculadora de Redução de Custos de Frota</h1>
  <p class="sub" {an("up", 1, 0.8)}>Enterprise Challenge FIAP e Sem Parar Empresas · Sprint 1</p>
  <div class="pills">{pills}</div>
  <p class="nomes" {an("fade", 2, 4.5, 1.0)}>{" · ".join(INTEGRANTES)} · Turma 1TIAO</p>
</div>"""


def cena_problema():
    fontes = ["Planilha de abastecimento", "Extrato de pedágio", "PDF da oficina", "Foto de multa", "Boleto de IPVA"]
    chips = "".join(f'<span class="chip-g" {an("pop", 1, i * 0.45)}>{f}</span>' for i, f in enumerate(fontes))
    probs = [("P1", "Dados fragmentados"), ("P2", "Custo absoluto não mede eficiência"),
             ("P3", "Custo alto nem sempre é desperdício"), ("P4", "Diagnóstico sem ação"),
             ("P5", "Dados incompletos no primeiro uso")]
    cards = "".join(f'<div class="card prob" {an("up", 3 + i)}><span class="cod">{c}</span><strong>{t}</strong></div>'
                    for i, (c, t) in enumerate(probs))
    return f"""
<blockquote><span {an("type", 0, 0, 4.6)}>"O gestor sabe quanto gastou — mas não onde está perdendo."</span>
  <cite {an("fade", 0, 4.6)}>Briefing Sem Parar Empresas</cite></blockquote>
<div class="chips">{chips}</div>
<div class="cinco">{cards}</div>"""


def cena_user_stories():
    visoes = [("Gestor de frota", 10), ("CFO e liderança", 4), ("Sem Parar Empresas", 6)]
    cont = "".join(f'<div class="card num" {an("up", 0, i * 0.8)}><div class="grande">'
                   f'{contador(q, "int", 0, i * 0.8 + 0.2, 1.0)}</div><div class="rot">{v}</div></div>'
                   for i, (v, q) in enumerate(visoes))
    prio = ["M"] * 7 + ["S", "M", "M"] + ["M"] * 4 + ["S", "C", "C", "M", "S", "S"]
    ids = [f"GF-{i:02d}" for i in range(1, 11)] + [f"CF-{i:02d}" for i in range(1, 5)] + \
          [f"SP-{i:02d}" for i in range(1, 7)]
    tiles = "".join(f'<span class="tile t{p}" {an("pop", 1, k * 0.12, 0.35)}>{i}</span>'
                    for k, (i, p) in enumerate(zip(ids, prio)))
    destaques = [("US-GF-09", "Sempre ter uma estimativa, mesmo com poucos dados"),
                 ("US-GF-10", "Receber perguntas sobre o que informar"),
                 ("US-GF-06", "Ver a economia em reais"),
                 ("US-SP-06", "Oportunidades comerciais para a Sem Parar Empresas")]
    lis = "".join(f'<li {an("left", 2, 0.6 + i * 2.6)}><span class="cod">{c}</span>{t}</li>'
                  for i, (c, t) in enumerate(destaques))
    return f"""
<div class="duas">
  <div>
    <div class="tres">{cont}</div>
    <div class="matriz" {an("fade", 1, 0)}>
      <div class="legenda-p"><span><i class="tM"></i>Must 14</span><span><i class="tS"></i>Should 4</span>
        <span><i class="tC"></i>Could 2</span></div>
      <div class="tiles">{tiles}</div>
      <p class="mudo">Matriz de rastreabilidade: funcionalidade, critério de aceite e Sprint prevista</p>
    </div>
  </div>
  <div><h3 {an("fade", 2)}>As quatro que definem o produto</h3><ul class="lista">{lis}</ul>
    <div class="selo-lgpd" {an("pop", 3, 0.3)}>LGPD: contato comercial só com base legal e preferência registrada</div>
  </div>
</div>"""


def cena_visao():
    caps = [("01", "Entender"), ("02", "Diagnosticar"), ("03", "Comparar"), ("04", "Otimizar"), ("05", "Acompanhar")]
    tiles = "".join(f'<div class="card cap" {an("up", 0, 1.6 + i * 0.75)}><span class="cod">{n}</span>'
                    f'<strong>{t}</strong></div>' for i, (n, t) in enumerate(caps))
    n2 = R["estimativa_EMP-A"]["niveis"]["2"]
    obs = n2["parcela_observada"]
    return f"""
<div class="cinco">{tiles}</div>
<h3 class="centro" {an("up", 1)}>Quanto se pode confiar em cada número?</h3>
<div class="faixa-demo">
  <div class="fx-rot" {an("fade", 2)}>Custo provável de 6 meses</div>
  <div class="fx-valor" {an("up", 2, 0.3)}>{mil(n2["p10"], 0)} a {mil(n2["p90"], 0)}</div>
  <div class="fx-barra" {an("fade", 2, 0.5)}>
    <div class="fx-obs" style="width:{obs * 100:.1f}%" {an("grow", 2, 1.2, 1.4)}></div>
  </div>
  <div class="fx-leg" {an("fade", 2, 2.4)}><span><i class="obs"></i>{obs * 100:.0f}% vem de documentos</span>
    <span><i class="est"></i>{(1 - obs) * 100:.0f}% estimado</span>
    <span class="selo">{ICONE["Baixa"]} Selo de confiança: Baixa (dados desatualizados)</span></div>
</div>"""


def cena_dados():
    sat = [("Arquivo de origem", 0, 0), ("Categoria", 560, 0), ("Veículo", 0, 400), ("Competência", 560, 400)]
    linhas = "".join(f'<path pathLength="1" {an("draw", 0, 0.8 + i * 0.5, 0.8)} d="M410 250 L{x + 120} {y + 35}" '
                     f'stroke="#c3c2b7" stroke-width="3" fill="none"/>' for i, (_, x, y) in enumerate(sat))
    nos = "".join(f'<div class="no" style="left:{x}px;top:{y}px" {an("pop", 0, 1.2 + i * 0.5)}>{t}</div>'
                  for i, (t, x, y) in enumerate(sat))
    status = ["observado", "corrigido", "imputado", "estimado", "não disponível"]
    chips = "".join(f'<span class="st" {an("pop", 0, 4.0 + i * 0.5)}>{s}</span>' for i, s in enumerate(status))
    frotas = [("EMP-A", 8), ("EMP-B", 30), ("EMP-C", 40)]
    fr = "".join(f'<div class="card frota" {an("up", 1, 0.3 + i * 0.5)}><span class="rot">{e} fictícia</span>'
                 f'<span class="grande">{contador(v, "int", 1, 0.5 + i * 0.5, 1.0)}</span>'
                 f'<span class="rot">veículos</span></div>' for i, (e, v) in enumerate(frotas))
    exemplos = ["Arquivo enviado duas vezes", "Odômetro errado", "Cobrança duplicada"]
    ex = "".join(f'<span class="chip-g" {an("pop", 1, 5.0 + i * 1.0)}>{e}</span>' for i, e in enumerate(exemplos))
    q = R["qualidade"]
    fora = len(q["marcacoes_fora_do_gabarito"])
    ok = ICONE["Alta"]
    return f"""
<div class="duas d-dados">
  <div class="modelo">
    <svg class="linhas" viewBox="0 0 800 500" aria-hidden="true">{linhas}</svg>
    {nos}
    <div class="no centro-no" {an("pop", 0, 0.2)}>Despesa<span>valor · data · categoria · origem · status</span></div>
    <div class="status">{chips}</div>
  </div>
  <div class="lado">
    <div class="tres">{fr}</div>
    <div class="card cenarios" {an("up", 1, 2.2)}><span class="grande">{contador(34, "int", 1, 2.4, 1.2)}</span>
      <span class="rot">situações planejadas, com gabarito</span><div class="exs">{ex}</div></div>
    <div class="resultado" {an("up", 2)}>{ok}<span>As 13 regras de qualidade detectaram todos os erros injetados ·
      {"nenhuma marcação" if fora == 0 else f"{fora} marcações"} fora do gabarito</span></div>
    <div class="aviso-t" {an("up", 3, 0.3)}>As regras foram escritas conhecendo os erros: isso prova a mecânica,
      não o desempenho com dados reais.</div>
  </div>
</div>"""


def cena_estimativa():
    est = R["estimativa_EMP-A"]
    real = est["valor_real_brl"]
    x0, x1, larg = 110_000, 160_000, 1180

    def px(v):
        return (v - x0) / (x1 - x0) * larg

    rotulos = ["N0 · composição da frota", "N1 · + duas respostas", "N2 · + extratos e notas",
               "N3 · + apólice, IPVA e multas"]
    cues = [(1, 0.4), (2, 0.4), (2, 2.4), (4, 0.3)]
    linhas = ""
    for k in range(4):
        nv = est["niveis"][str(k)]
        c, a = cues[k]
        dentro = nv["contem_valor_real"]
        marca = "" if dentro else f'<span class="fora" {an("pop", c, a + 1.4)}>{ICONE["Baixa"]} fora da faixa</span>'
        linhas += f"""
<div class="lin">
  <div class="lin-rot" {an("fade", c, a)}>{rotulos[k]}</div>
  <div class="lin-trilho">
    <div class="barra-f" style="left:{px(nv['p10']):.0f}px;width:{px(nv['p90']) - px(nv['p10']):.0f}px"
      {an("grow", c, a + 0.2, 1.0)}></div>
    <div class="p50" style="left:{px(nv['p50']):.0f}px" {an("pop", c, a + 1.1, 0.4)}></div>
  </div>
  <div class="lin-val" {an("fade", c, a + 0.9)}>{mil(nv["p10"], 0)} a {mil(nv["p90"], 0)} {marca}</div>
</div>"""
    marcas = "".join(f'<span style="left:{px(v):.0f}px">{mil(v, 0)}</span>' for v in range(110_000, 160_001, 10_000))
    perg = est["proximas_perguntas"][0]
    return f"""
<div class="grafico-est">
  <div class="eixo-real" style="left:{px(real) + 500:.0f}px" {an("fade", 0, 0.3)}>
    <span>valor real {mil(real, 0)}</span></div>
  {linhas}
  <div class="eixo-x" {an("fade", 0, 0.3)}>{marcas}</div>
</div>
<div class="duas inferior">
  <div class="card pergunta" {an("left", 3, 0.2)}><span class="rot">Próxima pergunta sugerida</span>
    <strong>{perg["pergunta"]}</strong>
    <span class="mudo">reduz a incerteza em cerca de {mil(perg["reducao_largura_brl"], 0)}</span></div>
  <div class="card ensaios" {an("left", 5, 0.8)}><span class="grande">{contador(280, "int", 5, 1.0, 1.2)}</span>
    <span class="rot">ensaios de calibração</span></div>
</div>"""


def cena_decomposicao():
    p = R["lmdi"]["pares_C-V01"]
    efeitos = [("Quilômetros", p["atividade"], "#2a78d6"), ("Consumo por km", p["intensidade"], "#eb6834"),
               ("Preço do litro", p["preco"], "#1baf7a"), ("Diferença total", p["diferenca"], "#0b0b0b")]
    escala = 190 / 80_000
    barras = ""
    for i, (nome, v, cor) in enumerate(efeitos):
        w = abs(v) * escala
        lado = "left:200px" if v >= 0 else f"left:{200 - w:.0f}px"
        sinal = "+" if v >= 0 else "-"
        barras += f"""
<div class="wf">
  <span class="wf-rot" {an("fade", 1, 0.3 + i * 0.9)}>{nome}</span>
  <div class="wf-tr"><div class="wf-b" style="{lado};width:{max(w, 3):.0f}px;background:{cor}"
    {an("grow" if v >= 0 else "growr", 1, 0.4 + i * 0.9, 0.8)}></div></div>
  <span class="wf-v" {an("fade", 1, 0.9 + i * 0.9)}>{sinal}{mil(abs(v), 1)}</span>
</div>"""
    serie = R["consumo_EMP-C"]["series"]["C-V07"]["cusum"]
    meses = list(serie)
    h = R["consumo_EMP-C"]["cusum_h"]
    W, H, ym = 760, 300, 22

    def xy(i, v):
        return 40 + i * (W - 60) / (len(meses) - 1), H - 30 - v / ym * (H - 60)

    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(i, serie[m]) for i, m in enumerate(meses)))
    ia = meses.index(R["consumo_EMP-C"]["alarmes"]["C-V07"])
    ax, ay = xy(ia, serie[meses[ia]])
    _, yh = xy(0, h)
    rot_m = "".join(f'<text x="{xy(i, 0)[0]:.0f}" y="{H - 6}" text-anchor="middle">{m[5:]}/{m[2:4]}</text>'
                    for i, m in enumerate(meses) if i % 2 == 0)
    pares = p["km_veiculo"] / p["km_ref"] - 1
    exc = R["consumo_EMP-C"]["excesso"][0]
    return f"""
<div class="equacao" {an("up", 0)}>Custo do combustível = <b class="c1">km rodados</b> × <b class="c2">litros por km</b>
  × <b class="c3">preço do litro</b></div>
<div class="duas d-dec">
  <div class="card">
    <h3 {an("fade", 1)}>C-V01 contra 27 caminhões parecidos</h3>
    <p class="mudo" {an("fade", 1, 0.2)}>Roda {pares * 100:.0f}% mais e faz {dec(p["km_l_veiculo"])} km/L contra
      {dec(p["km_l_ref"])} km/L: custa mais, mas é eficiente</p>
    <div class="wfs">{barras}<div class="wf-zero"></div></div>
  </div>
  <div class="card">
    <h3 {an("fade", 2)}>C-V07: queda de rendimento detectada</h3>
    <p class="mudo" {an("fade", 2, 0.2)}>{dec(exc["km_l_base"])} km/L para {dec(exc["km_l_recente"])} km/L ·
      soma acumulada (CUSUM)</p>
    <svg class="cusum" viewBox="0 0 {W} {H}" aria-hidden="true">
      <line x1="40" x2="{W - 20}" y1="{yh:.1f}" y2="{yh:.1f}" stroke="#d03b3b" stroke-width="1.5"
        stroke-dasharray="6 6" {an("fade", 2, 0.8)}/>
      <text x="44" y="{yh - 8:.1f}" class="lim" {an("fade", 2, 0.8)}>limite de alarme</text>
      <polyline pathLength="1" points="{pts}" fill="none" stroke="#2a78d6" stroke-width="3"
        stroke-linejoin="round" {an("draw", 2, 1.2, 3.2)}/>
      <circle cx="{ax:.1f}" cy="{ay:.1f}" r="9" fill="#d03b3b" stroke="#fcfcfb" stroke-width="3"
        {an("pop", 2, 2.7, 0.4)}/>
      <text x="{ax - 16:.1f}" y="{ay - 18:.1f}" text-anchor="end" class="alarme" {an("fade", 2, 2.9)}>alarme em fev/26</text>
      {rot_m}
    </svg>
    <p class="nota" {an("fade", 2, 4.5)}>3 de 3 quedas detectadas em 1 a 2 meses · nenhum alarme falso em 40 veículos</p>
  </div>
</div>"""


def cena_economia():
    c = R["oportunidades"]["EMP-C"]["cenarios"]
    b = R["oportunidades"]["EMP-B"]["cenarios"]
    nomes = [("conservador", "Conservador", "só oportunidades validadas", "#86b6ef"),
             ("base", "Base", "+ anomalias com evidência", "#2a78d6"),
             ("otimista", "Otimista", "+ hipóteses a validar", "#1c5cab")]
    maxv = max(c[k]["economia_liquida_anual"] for k, *_ in nomes)
    cols = ""
    for i, (k, n, d, cor) in enumerate(nomes):
        v = c[k]["economia_liquida_anual"]
        cols += f"""
<div class="col{' destaque' if k == 'base' else ''}">
  <div class="col-v" {an("fade", 0, 2.0 + i * 0.7)}>R$ {contador(round(v / 1000, 1), "dec1", 0, 2.0 + i * 0.7, 1.0)} mil</div>
  <div class="col-b" style="height:{v / maxv * 420:.0f}px;background:{cor}" {an("growy", 0, 1.8 + i * 0.7, 1.0)}></div>
  <div class="col-n"><strong>{n}</strong><span>{d}</span></div>
</div>"""
    fluxo = "".join(f'<span class="pill" {an("pop", 0, i * 0.6)}>{t}</span>' + (
        f'<span class="seta" {an("fade", 0, i * 0.6 + 0.3)}>→</span>' if i < 2 else "")
        for i, t in enumerate(["Achado", "Ação", "Economia líquida em R$"]))
    return f"""
<div class="fluxo-top">{fluxo}</div>
<div class="duas d-eco">
  <div class="card"><h3 {an("fade", 0, 1.4)}>EMP-C fictícia, 40 veículos · economia líquida por ano</h3>
    <div class="colunas">{cols}</div></div>
  <div class="lado">
    <div class="card realce" {an("left", 1, 0.2)}><span class="rot">EMP-C, cenário-base</span>
      <span class="grande">cerca de {mil(c["base"]["economia_liquida_anual"], 0)}</span>
      <span class="mudo">por ano, já descontado o custo de executar o plano</span></div>
    <div class="card negativo" {an("left", 2, 0.2)}><span class="rot">EMP-B fictícia, 30 veículos · cenário-base</span>
      <span class="grande">{mil(b["base"]["economia_liquida_anual"], 1)}</span>
      <span class="mudo">executar o plano custa mais do que ele economiza</span></div>
    <p class="frase" {an("up", 3, 0.2)}>A calculadora não precisa inventar economia.</p>
  </div>
</div>"""


def cena_arquitetura():
    etapas = ["Entrada de dados", "Tratamento e organização", "Análise dos custos", "Diagnóstico", "Benchmark",
              "Recomendações", "Visualização e relatório"]
    nos = ""
    for i, e in enumerate(etapas):
        nos += f'<div class="etapa" {an("pop", 0, 0.3 + i * 0.9, 0.5)}><span class="cod">{i + 1}</span>{e}</div>'
        if i < len(etapas) - 1:
            nos += f'<div class="seta-h" {an("grow", 0, 0.7 + i * 0.9, 0.4)}></div>'
    tec = [("Python e FastAPI", "monólito modular"), ("PostgreSQL", "isolamento por cliente"),
           ("Processo separado", "leitura de documentos"), ("Relatório em PDF", "painéis por perfil")]
    t = "".join(f'<div class="card tec" {an("up", 0, 6.8 + i * 0.5)}><strong>{a}</strong><span>{b}</span></div>'
                for i, (a, b) in enumerate(tec))
    return f"""
<div class="fluxo">{nos}</div>
<div class="quatro">{t}</div>
<div class="duas d-ia">
  <div class="card ia" {an("up", 1, 0.2)}><strong>Cálculos financeiros</strong><span>determinísticos e versionados</span></div>
  <div class="card ia" {an("up", 1, 2.2)}><strong>Inteligência artificial</strong><span>lê documentos e explica; não calcula valores</span></div>
</div>"""


def cena_proximos():
    sprints = [("Sprint 1", "Especificação", "esta entrega"), ("Sprint 2", "Ingestão e primeira estimativa", ""),
               ("Sprint 3", "Diagnóstico, benchmark e recomendações", ""), ("Sprint 4", "Protótipo testado com gestores", "")]
    itens = "".join(f'<div class="sp" {an("up", 0, 0.2 + i * 1.6)}><i class="{"on" if i == 0 else ""}"></i>'
                    f'<span class="cod">{s}</span><strong>{t}</strong><span class="mudo">{x}</span></div>'
                    for i, (s, t, x) in enumerate(sprints))
    return f"""
<div class="linha-t"><div class="trilho-t" {an("grow", 0, 0, 5.4)}></div>{itens}</div>
<div class="card repo" {an("up", 1, 0)}><span class="rot">Documentação completa no repositório</span>
  <strong>{REPO}</strong></div>
<div class="obrigado" {an("up", 2, 0)}>Obrigado.</div>
<p class="nomes centro" {an("fade", 2, 0.6)}>{" · ".join(INTEGRANTES)}</p>"""


CENAS = [cena_abertura, cena_problema, cena_user_stories, cena_visao, cena_dados, cena_estimativa,
         cena_decomposicao, cena_economia, cena_arquitetura, cena_proximos]
TITULOS = ["Abertura", "O problema", "User Stories", "Visão do produto", "Dados", "Estimativa progressiva",
           "Custo alto não é desperdício", "Economia em três cenários", "Arquitetura", "Próximos passos"]

CSS = """
html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: var(--pagina); }
#palco { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
.cena { position: absolute; inset: 0; padding: 150px 110px 90px; opacity: 0; display: flex; flex-direction: column;
  gap: 40px; }
.cena h2 { position: absolute; top: 64px; left: 110px; font-size: 30px; color: var(--tinta-2); font-weight: 600; }
.cena h2 .cod { margin-right: 14px; }
#topo { position: absolute; top: 56px; right: 110px; font-size: 22px; z-index: 5; }
#topo .marca { font-size: 26px; }
#barra { position: absolute; left: 0; bottom: 0; height: 6px; background: var(--pulso); width: 0; z-index: 5; }
#marcas-barra { position: absolute; left: 0; right: 0; bottom: 0; height: 6px; background: var(--linha); z-index: 4; }
#marcas-barra i { position: absolute; top: 0; width: 2px; height: 6px; background: var(--pagina); }
h1 { font-size: 92px; line-height: 1.04; letter-spacing: -0.02em; margin: 0; }
h3 { font-size: 34px; margin: 0 0 18px; }
p, li { font-size: 30px; }
.mudo { color: var(--mudo); } .centro { text-align: center; }
.cod { font-family: var(--fonte-titulo); font-weight: 600; color: var(--pulso-escuro); }
.card { background: var(--superficie); border: 1px solid var(--linha); border-radius: 14px; padding: 28px 32px; }
.rot { font-size: 24px; color: var(--tinta-2); }
.card span.mudo, .card .mudo { font-size: 24px; }
.grande { font-family: var(--fonte-titulo); font-weight: 600; font-size: 72px; letter-spacing: -0.02em; line-height: 1.05; }
.duas { display: grid; grid-template-columns: 1fr 1fr; gap: 56px; }
.tres { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.quatro { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.cinco { display: grid; grid-template-columns: repeat(5, 1fr); gap: 24px; }
.pill { display: inline-flex; align-items: center; height: 64px; padding: 0 30px; border-radius: 999px;
  border: 2px solid var(--pulso); color: var(--pulso-escuro); font-size: 30px; font-weight: 600; background: var(--superficie); }
.chip-g { display: inline-flex; align-items: center; height: 54px; padding: 0 24px; border-radius: 12px;
  border: 1px solid var(--eixo); font-size: 26px; background: var(--superficie); }
/* abertura */
.abertura { position: relative; display: flex; flex-direction: column; gap: 30px; margin-top: 40px; }
.pulso-grande { position: absolute; left: -110px; top: 690px; width: 1920px; height: 220px; opacity: .35; }
.marca.enorme { font-size: 76px; gap: 20px; }
.abertura .sub { font-size: 38px; color: var(--tinta-2); margin: 0; }
.pills { display: flex; gap: 22px; margin-top: 24px; }
.nomes { font-size: 26px; color: var(--tinta-2); margin-top: 30px; }
.nomes.centro { margin-top: 10px; }
/* problema */
blockquote { margin: 0; font-family: var(--fonte-titulo); font-size: 64px; line-height: 1.15; letter-spacing: -0.01em;
  border-left: 6px solid var(--pulso); padding-left: 40px; max-width: 1600px; min-height: 160px; }
cite { display: block; font-family: var(--fonte); font-style: normal; font-size: 26px; color: var(--mudo); margin-top: 16px; }
.chips { display: flex; gap: 18px; flex-wrap: wrap; }
.prob { display: flex; flex-direction: column; gap: 14px; min-height: 260px; }
.prob .cod { font-size: 30px; } .prob strong { font-size: 32px; line-height: 1.2; }
/* user stories */
.num .grande { font-size: 96px; } .num .rot { font-size: 26px; }
.matriz { margin-top: 36px; }
.tiles { display: grid; grid-template-columns: repeat(10, 1fr); gap: 10px; margin: 18px 0; }
.tile { height: 64px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 19px;
  font-weight: 600; color: #fff; }
.tM, .legenda-p .tM { background: #2a78d6; } .tS, .legenda-p .tS { background: #eb6834; } .tC, .legenda-p .tC { background: #1baf7a; }
.tile.tC, .tile.tS { color: #0b0b0b; }
.legenda-p { display: flex; gap: 28px; font-size: 24px; color: var(--tinta-2); }
.legenda-p i { display: inline-block; width: 18px; height: 18px; border-radius: 5px; margin-right: 10px; vertical-align: -2px; }
.lista { list-style: none; padding: 0; margin: 0; }
.lista li { padding: 22px 0; border-bottom: 1px solid var(--linha); display: flex; gap: 20px; align-items: baseline; }
.lista .cod { min-width: 150px; font-size: 28px; }
.selo-lgpd { margin-top: 30px; display: inline-block; padding: 18px 26px; border-radius: 12px; font-size: 26px;
  border: 2px solid var(--bom); color: var(--bom-texto); background: var(--superficie); font-weight: 600; }
/* visão */
.cap { display: flex; flex-direction: column; gap: 10px; } .cap .cod { font-size: 26px; } .cap strong { font-size: 40px; }
h3.centro { font-size: 52px; margin-top: 30px; }
.faixa-demo { width: 1300px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
.fx-rot { font-size: 26px; color: var(--tinta-2); } .fx-valor { font-family: var(--fonte-titulo); font-size: 66px; font-weight: 600; }
.fx-barra { height: 40px; border-radius: 10px; background: var(--pulso-100); overflow: hidden; }
.fx-obs { height: 100%; background: var(--pulso); border-radius: 10px 0 0 10px; }
.fx-leg { display: flex; gap: 40px; font-size: 26px; color: var(--tinta-2); align-items: center; }
.fx-leg i { display: inline-block; width: 20px; height: 20px; border-radius: 5px; margin-right: 10px; vertical-align: -3px; }
.fx-leg i.obs { background: var(--pulso); } .fx-leg i.est { background: var(--pulso-100); }
.fx-leg .selo { margin-left: auto; color: var(--tinta); font-size: 26px; }
.selo svg { width: 28px; height: 28px; }
/* dados */
.d-dados { grid-template-columns: 1.05fr 1fr; }
.modelo { position: relative; height: 760px; }
.linhas { position: absolute; left: 0; top: 0; width: 800px; height: 500px; }
.no { position: absolute; width: 240px; padding: 18px 20px; background: var(--superficie); border: 2px solid var(--eixo);
  border-radius: 12px; font-size: 28px; font-weight: 600; text-align: center; }
.centro-no { left: 210px; top: 170px; width: 400px; border: 3px solid var(--pulso); font-size: 40px; }
.centro-no span { display: block; font-size: 21px; font-weight: 400; color: var(--tinta-2); margin-top: 6px; }
.status { position: absolute; left: 0; width: 800px; top: 540px; display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; }
.st { padding: 10px 20px; border-radius: 999px; font-size: 24px; background: var(--pulso-100); color: var(--pulso-escuro); font-weight: 600; }
.lado { display: flex; flex-direction: column; gap: 24px; }
.frota { display: flex; flex-direction: column; gap: 4px; padding: 22px 26px; }
.cenarios { display: flex; flex-direction: column; gap: 6px; } .exs { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px; }
.exs .chip-g { font-size: 22px; height: 46px; }
.resultado { display: flex; gap: 16px; align-items: center; font-size: 28px; font-weight: 600; }
.resultado svg { width: 40px; height: 40px; flex: none; }
.aviso-t { font-size: 26px; color: var(--tinta-2); border-left: 4px solid var(--serio); padding-left: 18px; }
/* estimativa */
.grafico-est { position: relative; height: 560px; }
.lin { display: grid; grid-template-columns: 500px 1200px; height: 110px; align-items: center; position: relative; }
.lin-rot { font-size: 28px; font-weight: 600; }
.lin-trilho { position: relative; height: 44px; }
.barra-f { position: absolute; top: 0; height: 44px; border-radius: 10px; background: var(--pulso); opacity: .85; }
.p50 { position: absolute; top: -6px; width: 6px; height: 56px; margin-left: -3px; background: var(--tinta); border-radius: 3px; }
.lin-val { position: absolute; left: 500px; top: 80px; font-size: 22px; color: var(--tinta-2); white-space: nowrap; }
.fora { margin-left: 16px; color: var(--tinta); font-weight: 600; } .fora svg { width: 22px; height: 22px; vertical-align: -4px; }
.eixo-real { position: absolute; top: -20px; bottom: 50px; border-left: 3px dashed var(--tinta); z-index: 2; }
.eixo-real span { position: absolute; top: -34px; left: -120px; width: 240px; text-align: center; font-size: 22px; font-weight: 600; }
.eixo-x { position: absolute; left: 500px; width: 1180px; bottom: 0; height: 30px; border-top: 1px solid var(--eixo); }
.eixo-x span { position: absolute; top: 8px; transform: translateX(-50%); font-size: 20px; color: var(--mudo); white-space: nowrap; }
.inferior { grid-template-columns: 1.4fr 1fr; }
.pergunta { display: flex; flex-direction: column; gap: 8px; } .pergunta strong { font-size: 36px; }
.ensaios { display: flex; align-items: center; gap: 24px; }
/* decomposição */
.equacao { font-family: var(--fonte-titulo); font-size: 46px; font-weight: 600; text-align: center; }
.equacao .c1 { color: #1c5cab; } .equacao .c2 { color: #b9471a; } .equacao .c3 { color: #087a54; }
.d-dec { gap: 40px; } .d-dec .card { padding: 30px; } .d-dec p { font-size: 25px; margin: 0 0 20px; }
.wfs { position: relative; display: flex; flex-direction: column; gap: 22px; margin-top: 16px; }
.wf { display: grid; grid-template-columns: 220px 400px 1fr; align-items: center; }
.wf-rot { font-size: 24px; } .wf-v { font-size: 24px; font-weight: 600; text-align: right; white-space: nowrap; }
.wf-tr { position: relative; height: 34px; }
.wf-b { position: absolute; top: 0; height: 34px; border-radius: 6px; }
.wf-zero { position: absolute; left: 420px; top: -6px; bottom: -6px; border-left: 2px solid var(--eixo); }
.cusum { width: 100%; height: 320px; } .cusum text { font-size: 18px; fill: var(--mudo); }
.cusum .lim { fill: #b02a2a; font-size: 18px; } .cusum .alarme { fill: var(--tinta); font-size: 22px; font-weight: 600; }
.nota { font-size: 24px !important; color: var(--tinta-2); }
/* economia */
.fluxo-top { display: flex; gap: 18px; align-items: center; justify-content: center; }
.seta { font-size: 40px; color: var(--mudo); }
.d-eco { grid-template-columns: 1.2fr 1fr; }
.colunas { display: flex; gap: 40px; align-items: flex-end; height: 560px; padding: 0 20px; border-bottom: 2px solid var(--eixo); }
.col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 12px; position: relative; }
.col-b { width: 100%; max-width: 150px; border-radius: 10px 10px 0 0; }
.col-v { font-size: 30px; font-weight: 600; }
.col-n { position: absolute; top: calc(100% + 10px); text-align: center; display: flex; flex-direction: column; }
.col-n strong { font-size: 26px; } .col-n span { font-size: 20px; color: var(--tinta-2); }
.realce, .negativo { display: flex; flex-direction: column; gap: 6px; }
.realce { border: 2px solid var(--pulso); } .negativo { border-left: 6px solid var(--serio); }
.frase { font-family: var(--fonte-titulo); font-size: 44px; font-weight: 600; margin: 10px 0 0; }
/* arquitetura */
.fluxo { display: flex; align-items: center; justify-content: space-between; margin-top: 30px; }
.etapa { width: 210px; height: 150px; border: 2px solid var(--pulso); border-radius: 14px; background: var(--superficie);
  display: flex; flex-direction: column; justify-content: center; padding: 0 16px; font-size: 23px; font-weight: 600; line-height: 1.2; gap: 8px; }
.etapa .cod { font-size: 24px; }
.seta-h { width: 34px; height: 4px; background: var(--eixo); }
.tec { display: flex; flex-direction: column; gap: 6px; } .tec strong { font-size: 30px; } .tec span { font-size: 24px; color: var(--tinta-2); }
.d-ia .ia { display: flex; flex-direction: column; gap: 8px; } .ia strong { font-size: 36px; } .ia span { font-size: 28px; color: var(--tinta-2); }
.d-ia .ia:first-child { border-left: 6px solid var(--pulso); } .d-ia .ia:last-child { border-left: 6px solid #1baf7a; }
/* próximos */
.linha-t { position: relative; display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; margin-top: 40px; }
.trilho-t { position: absolute; left: 0; right: 0; top: 14px; height: 4px; background: var(--eixo); }
.sp { position: relative; display: flex; flex-direction: column; gap: 10px; padding-top: 50px; }
.sp i { position: absolute; top: 0; left: 0; width: 32px; height: 32px; border-radius: 50%; background: var(--superficie);
  border: 4px solid var(--eixo); } .sp i.on { background: var(--pulso); border-color: var(--pulso); }
.sp .cod { font-size: 28px; } .sp strong { font-size: 40px; line-height: 1.15; } .sp .mudo { font-size: 24px; }
.repo { display: flex; flex-direction: column; gap: 6px; } .repo strong { font-size: 40px; }
.obrigado { font-family: var(--fonte-titulo); font-size: 110px; font-weight: 600; text-align: center; margin-top: 10px; }
/* pré e guia */
#pre { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 6; }
#pre .marca { font-size: 90px; gap: 24px; }
#contagem { position: absolute; left: 0; right: 0; top: 640px; text-align: center; font-size: 34px; color: var(--tinta-2); display: none; }
#legenda { position: absolute; left: 110px; right: 110px; bottom: 30px; z-index: 7; display: none; background: rgba(11,11,11,.86);
  color: #fff; border-radius: 12px; padding: 18px 26px; font-size: 30px; line-height: 1.35; }
#legenda .prox { display: block; color: #c3c2b7; font-size: 22px; margin-top: 8px; }
body.guia #legenda, body.guia #contagem { display: block; }
"""

JS = """
const CUES = __CUES__;
const TOTAL = __TOTAL__;
const cenas = [...document.querySelectorAll('.cena')];
const clamp = (x) => Math.max(0, Math.min(1, x));
const ease = (p) => 1 - Math.pow(1 - p, 3);
const easeIO = (p) => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const fmt = (v, f) => f === 'int' ? Math.round(v).toLocaleString('pt-BR')
  : v.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1});
cenas.forEach((c, i) => c.querySelectorAll('[data-a]').forEach(el => {
  const cue = CUES[i].cues[+el.dataset.c] || CUES[i].cues[0];
  el._t0 = cue.ini + (+el.dataset.dl); el._d = +el.dataset.d;
  if (el.dataset.a === 'type') { el._txt = el.textContent; }
}));
window.render = function (t) {
  document.getElementById('barra').style.width = (clamp(t / TOTAL) * 100) + '%';
  const pre = document.getElementById('pre');
  pre.style.opacity = t < CUES[0].ini ? 1 : clamp(1 - (t - CUES[0].ini) / 0.5);
  const cont = document.getElementById('contagem');
  cont.textContent = t < CUES[0].ini ? 'Comece a narrar em ' + Math.ceil(CUES[0].ini - t) : '';
  cenas.forEach((c, i) => {
    const ini = CUES[i].ini, fim = CUES[i].fim, ultima = i === cenas.length - 1;
    let o = clamp((t - ini) / 0.5);
    if (!ultima) o = Math.min(o, clamp((fim - t) / 0.45));
    c.style.opacity = o;
    c.style.visibility = o > 0 ? 'visible' : 'hidden';
    if (o === 0) return;
    c.querySelectorAll('[data-a]').forEach(el => {
      const p = clamp((t - el._t0) / el._d), e = ease(p);
      switch (el.dataset.a) {
        case 'up': el.style.opacity = e; el.style.transform = `translateY(${(1 - e) * 36}px)`; break;
        case 'left': el.style.opacity = e; el.style.transform = `translateX(${(1 - e) * 60}px)`; break;
        case 'fade': el.style.opacity = e; break;
        case 'pop': el.style.opacity = e; el.style.transform = `scale(${0.85 + 0.15 * ease(clamp(p * 1.2))})`; break;
        case 'grow': el.style.transformOrigin = 'left center'; el.style.transform = `scaleX(${easeIO(p)})`; break;
        case 'growr': el.style.transformOrigin = 'right center'; el.style.transform = `scaleX(${easeIO(p)})`; break;
        case 'growy': el.style.transformOrigin = 'center bottom'; el.style.transform = `scaleY(${easeIO(p)})`; break;
        case 'draw': el.style.strokeDasharray = 1; el.style.strokeDashoffset = 1 - easeIO(p); break;
        case 'count': el.textContent = fmt(+el.dataset.de + (+el.dataset.ate - +el.dataset.de) * e, el.dataset.fmt); break;
        case 'type': el.textContent = el._txt.slice(0, Math.round(el._txt.length * p));
                     el.style.opacity = p > 0 ? 1 : 0; break;
      }
    });
  });
  const leg = document.getElementById('legenda');
  let atual = null, prox = null;
  const todas = CUES.flatMap(b => b.cues);
  for (let k = 0; k < todas.length; k++) {
    if (t >= todas[k].ini - 0.25 && (k + 1 >= todas.length || t < todas[k + 1].ini - 0.25)) { atual = todas[k]; prox = todas[k + 1]; break; }
  }
  if (t < CUES[0].ini) { atual = null; prox = todas[0]; }
  leg.innerHTML = (atual ? atual.texto : '') + (prox ? `<span class="prox">a seguir: ${prox.texto}</span>` : '');
  leg.style.visibility = (atual || prox) ? 'visible' : 'hidden';
};
if (new URLSearchParams(location.search).has('guia')) document.body.classList.add('guia');
const tq = new URLSearchParams(location.search).get('t');
render(tq ? +tq : 0);
"""


def main():
    blocos = blocos_do_roteiro()
    assert len(blocos) == len(CENAS), f"roteiro tem {len(blocos)} blocos e o vídeo tem {len(CENAS)} cenas"
    total = cronometrar(blocos)
    cenas = ""
    for i, (b, f) in enumerate(zip(blocos, CENAS)):
        h2 = f'<h2><span class="cod">{i + 1:02d}</span>{TITULOS[i]}</h2>' if i else ""
        cenas += f'<section class="cena" id="c{i + 1}">{h2}{f()}</section>'
    marcas = "".join(f'<i style="left:{b["ini"] / total * 100:.2f}%"></i>' for b in blocos[1:])
    cues = [{"ini": b["ini"], "fim": b["fim"], "cues": b["cues"]} for b in blocos]
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Frota Pulse — vídeo da Sprint 1</title>
<link rel="stylesheet" href="estilo.css"><style>{CSS}</style></head>
<body><div id="palco">
<div id="topo"><div class="marca">{PULSO.format(w=40, h=24, cor="#2a78d6")}<span>frota <b>pulse</b></span></div></div>
{cenas}
<div id="pre"><div class="marca">{PULSO.format(w=96, h=58, cor="#2a78d6")}<span>frota <b>pulse</b></span></div></div>
<div id="contagem"></div><div id="legenda"></div>
<div id="marcas-barra">{marcas}</div><div id="barra"></div>
</div>
<script>{JS.replace("__CUES__", json.dumps(cues, ensure_ascii=False)).replace("__TOTAL__", f"{total:.2f}")}</script>
</body></html>
"""
    (SAIDA / "video.html").write_text(html, encoding="utf-8")
    (SAIDA / "video-tempos.json").write_text(json.dumps({"total": round(total, 2), "fps": 30, "blocos": cues},
                                                        ensure_ascii=False, indent=1), encoding="utf-8")

    srt, n = [], 1
    for b in blocos:
        for c in b["cues"]:
            srt.append(f"{n}\n{srt_tempo(c['ini'])} --> {srt_tempo(c['fim'])}\n{c['texto']}\n")
            n += 1
    (RAIZ / "docs" / "video" / "legendas.srt").write_text("\n".join(srt), encoding="utf-8")

    linhas = ["# Narração do vídeo da Sprint 1", "",
              "Texto da narração do vídeo, que também alimenta a animação. Para mudar uma frase, edite a tabela e rode "
              "`python src/gerar_video.py`: os tempos se ajustam.", "",
              f"**Duração total: {mmss(total)}.** A fala começa em {mmss(PRE)}, depois da contagem regressiva, "
              f"no ritmo de {PPM} palavras por minuto. Cada linha mostra o instante em que a frase começa na animação.",
              "", "| Início | Frase |", "|---|---|"]
    for i, b in enumerate(blocos):
        linhas.append(f"| **{mmss(b['ini'])}** | **Cena {i + 1}: {TITULOS[i]}** |")
        for c in b["cues"]:
            linhas.append(f"| {mmss(c['ini'])} | {c['texto']} |")
    (RAIZ / "docs" / "video" / "narracao.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"ok: video.html, narracao.md, legendas.srt · duração {mmss(total)} ({total:.1f} s)")


if __name__ == "__main__":
    main()

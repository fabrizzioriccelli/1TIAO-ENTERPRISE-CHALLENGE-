#!/usr/bin/env python3
"""Gera as páginas HTML da capa e dos wireframes CONCEITUAIS a partir dos resultados calculados.

Saída: assets/fontes/*.html (editáveis). As imagens PNG em assets/ são capturas dessas páginas, feitas com um
navegador sem interface (comando no README de assets/). Os números vêm de data/resultados/exemplos-calculados.json,
portanto coincidem com a documentação. Wireframes não são interface implementada.

Uso:
    python src/gerar_visuais.py
"""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
R = json.loads((RAIZ / "data" / "resultados" / "exemplos-calculados.json").read_text(encoding="utf-8"))
SAIDA = RAIZ / "assets" / "fontes"

PULSO = ('<svg width="{w}" height="{h}" viewBox="0 0 40 24" aria-hidden="true"><path d="M2 16 H12 L16 7 L20 19 '
         'L24 12 H38" fill="none" stroke="{cor}" stroke-width="2.6" stroke-linecap="round" '
         'stroke-linejoin="round"/></svg>')
ICONE = {
    "Alta": ('<svg width="16" height="16" viewBox="-8 -8 16 16"><circle r="7" fill="none" stroke="#0ca30c" '
             'stroke-width="1.6"/><path d="M-3.5 0 L-1 2.6 L3.6 -2.6" stroke="#0ca30c" stroke-width="1.8" fill="none" '
             'stroke-linecap="round"/></svg>'),
    "Moderada": ('<svg width="16" height="16" viewBox="-8 -8 16 16"><circle r="7" fill="none" stroke="#c98500" '
                 'stroke-width="1.6"/><path d="M-3.5 0 H3.5" stroke="#c98500" stroke-width="1.8" '
                 'stroke-linecap="round"/></svg>'),
    "Baixa": ('<svg width="16" height="16" viewBox="-8 -8 16 16"><circle r="7" fill="none" stroke="#ec835a" '
              'stroke-width="1.6"/><path d="M0 -3.8 V0.8 M0 3.4 V3.6" stroke="#ec835a" stroke-width="1.8" '
              'stroke-linecap="round"/></svg>'),
    "Insuficiente": ('<svg width="16" height="16" viewBox="-8 -8 16 16"><circle r="7" fill="none" stroke="#d03b3b" '
                     'stroke-width="1.6"/><path d="M-2.8 -2.8 L2.8 2.8 M2.8 -2.8 L-2.8 2.8" stroke="#d03b3b" '
                     'stroke-width="1.8" stroke-linecap="round"/></svg>'),
}
ESTAGIO = {"observacao": 1, "anomalia": 2, "hipotese": 2, "oportunidade_validada": 4}
NOME_ESTAGIO = {"observacao": "Observação", "anomalia": "Anomalia", "hipotese": "Hipótese",
                "oportunidade_validada": "Oportunidade validada"}


def brl(v, casas=0):
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s


def mil(v, casas=1):
    return ("-" if v < 0 else "") + "R$ " + f"{abs(v) / 1000:.{casas}f}".replace(".", ",") + " mil"


def mi(v, casas=2):
    return "R$ " + f"{v / 1e6:.{casas}f}".replace(".", ",") + " mi"


def pct(v, casas=1):
    return f"{100 * v:.{casas}f}%".replace(".", ",")


def dec(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def pagina(titulo, corpo, largura, extra_css=""):
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title><link rel="stylesheet" href="estilo.css">
<style>body {{ width: {largura}px; position: relative; }} {extra_css}</style></head>
<body>{corpo}</body></html>
"""


def estagio_html(estagio):
    n = ESTAGIO[estagio]
    pontos = "".join(f'<i class="on{k + 1}"></i>' if k < n else "<i></i>" for k in range(4))
    return f'<span class="estagio" aria-hidden="true">{pontos}</span> {NOME_ESTAGIO[estagio]}'


def capa():
    caps = [("01", "Understand", "Entender", "Documentos em qualquer formato, com origem e status de cada valor"),
            ("02", "Diagnose", "Diagnosticar", "Custo total, indicadores normalizados e desvios com evidência"),
            ("03", "Compare", "Comparar", "Histórico, pares e referências, só quando há equivalência"),
            ("04", "Optimize", "Otimizar", "Ações com economia em R$ por cenário e um próximo passo"),
            ("05", "Monitor", "Acompanhar", "Atualização mensal e economia realizada medida")]
    itens = "".join(f"""<li><span class="n">{n}</span><div><strong>{en}</strong> <span class="pt">{pt}</span>
      <p>{d}</p></div></li>""" for n, en, pt, d in caps)
    corpo = f"""
<div class="capa">
  <svg class="fundo" viewBox="0 0 1600 640" preserveAspectRatio="none" aria-hidden="true">
    <path d="M0 520 H520 L580 420 L640 565 L700 480 H1600" fill="none" stroke="#cde2fb" stroke-width="3"
      stroke-linejoin="round"/></svg>
  <div class="esq">
    <div class="marca">{PULSO.format(w=46, h=28, cor="#2a78d6")}<span>frota <b>pulse</b></span></div>
    <h1>Inteligência de custos que<br>transforma dados em decisões</h1>
    <p class="sub">Calculadora de Redução de Custos de Frota. Proposta acadêmica para o Enterprise Challenge
    FIAP e Sem Parar Empresas, Sprint 1.</p>
  </div>
  <ol class="caps">{itens}</ol>
  <p class="rodape">Conceito acadêmico. Não é produto oficial da Sem Parar Empresas, da Corpay nem da FIAP.</p>
</div>"""
    css = """
.capa { width: 1600px; height: 640px; padding: 72px 80px; position: relative; overflow: hidden; display: grid;
  grid-template-columns: 1fr 560px; gap: 64px; background: var(--pagina); }
.fundo { position: absolute; inset: 0; width: 100%; height: 100%; }
.esq, .caps, .rodape { position: relative; }
.capa .marca { font-size: 28px; }
.capa h1 { font-size: 54px; line-height: 1.08; margin-top: 56px; }
.sub { font-size: 18px; color: var(--tinta-2); max-width: 620px; margin-top: 24px; }
.caps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; align-self: center; }
.caps li { display: grid; grid-template-columns: 44px 1fr; gap: 12px; background: var(--superficie);
  border: 1px solid var(--linha); border-radius: 10px; padding: 14px 18px; }
.caps .n { font-family: var(--fonte-titulo); font-weight: 600; color: var(--pulso); font-size: 18px; }
.caps strong { font-size: 16px; } .caps .pt { color: var(--tinta-2); font-size: 14px; }
.caps p { margin: 2px 0 0; font-size: 13px; color: var(--tinta-2); }
.rodape { position: absolute; left: 80px; bottom: 28px; font-size: 13px; color: var(--mudo); margin: 0; }
"""
    return pagina("Frota Pulse — capa", corpo, 1600, css)


def wf_estimativa():
    est = R["estimativa_EMP-A"]["niveis"]
    n0, n1 = est["0"], est["1"]
    lo, hi = 100_000, 170_000
    def pos(v):
        return 100 * (v - lo) / (hi - lo)
    cats = [("Combustível", "estimado"), ("Locação de 2 automóveis", "estimado"), ("Manutenção", "estimado"),
            ("Seguro", "estimado"), ("IPVA e licenciamento", "estimado"), ("Pedágio", "estimado"),
            ("Multas", "estimado"), ("Outros", "estimado")]
    linhas = "".join(f'<tr><td>{c}</td><td><span class="chip">{s}</span></td>'
                     f'<td class="num">{brl(n0["componentes_p50"][k], 0)}</td></tr>'
                     for (c, s), k in zip(cats, ["combustivel", "locacao", "manutencao", "seguro", "tributos",
                                                 "pedagio", "multas", "outros"]))
    corpo = f"""
<div class="aviso">Wireframe conceitual · dados sintéticos · não é interface implementada</div>
<header class="topo"><div class="marca">{PULSO.format(w=34, h=20, cor="#2a78d6")}<span>frota <b>pulse</b></span></div>
  <span class="sec">Empresa Sintética A (fictícia)</span></header>
<main class="grade">
  <aside class="cartao">
    <h3>Sua frota</h3>
    <dl><dt>Veículos</dt><dd>8</dd><dt>Utilitários próprios</dt><dd>4</dd><dt>Automóveis próprios</dt><dd>2</dd>
    <dt>Automóveis locados</dt><dd>2</dd><dt>Operação</dt><dd>Serviços técnicos urbanos</dd><dt>UF</dt><dd>SP</dd></dl>
    <p class="mudo pequeno">3 perguntas respondidas · nenhum documento enviado</p>
  </aside>
  <section class="cartao principal">
    <p class="rotulo">Custo total estimado · out/2025 a mar/2026</p>
    <p class="heroi">{mil(n0['p50'], 0)}</p>
    <p class="sec">Provavelmente entre <strong>{mil(n0['p10'], 0)}</strong> e <strong>{mil(n0['p90'], 0)}</strong>.
       Ainda é uma estimativa só com premissas.</p>
    <div class="faixa" role="img" aria-label="Faixa de {mil(n0['p10'], 0)} a {mil(n0['p90'], 0)}">
      <div class="trilho"></div>
      <div class="banda" style="left:{pos(n0['p10']):.1f}%; width:{pos(n0['p90']) - pos(n0['p10']):.1f}%"></div>
      <div class="ponto" style="left:{pos(n0['p50']):.1f}%"></div>
    </div>
    <div class="escala tab"><span>R$ 100 mil</span><span>R$ 135 mil</span><span>R$ 170 mil</span></div>
    <div class="linha-selo">
      <span class="selo">{ICONE['Insuficiente']} Confiança: insuficiente</span>
      <span class="chip">0% do valor vem de documentos</span>
    </div>
    <table><thead><tr><th>Categoria</th><th>Situação</th><th class="num">Valor central</th></tr></thead>
    <tbody>{linhas}</tbody></table>
  </section>
  <aside class="cartao pergunta">
    <p class="rotulo">Próximas perguntas</p>
    <h3>Quanto a frota gasta com combustível por mês?</h3>
    <div class="campo">R$ por mês</div>
    <h3 class="seg">Quantos km cada veículo roda por mês, em média?</h3>
    <div class="campo">km por mês</div>
    <p class="ganho">Responder às duas reduz a largura da faixa de <strong>{mil(n0['largura_p10_p90'], 1)}</strong>
       para <strong>{mil(n1['largura_p10_p90'], 1)}</strong>.</p>
    <span class="botao">Responder</span> <span class="botao sec">Enviar extratos</span>
  </aside>
</main>"""
    css = """
body { height: 900px; padding-top: 30px; }
.topo { display: flex; justify-content: space-between; align-items: center; padding: 18px 32px;
  border-bottom: 1px solid var(--linha); background: var(--superficie); }
.grade { display: grid; grid-template-columns: 260px 1fr 360px; gap: 20px; padding: 24px 32px; }
dl { display: grid; grid-template-columns: 1fr auto; gap: 8px 12px; margin: 16px 0; font-size: 14px; }
dt { color: var(--tinta-2); } dd { margin: 0; text-align: right; font-weight: 500; }
.pequeno { font-size: 12px; }
.heroi { font-family: var(--fonte-titulo); font-weight: 600; font-size: 56px; letter-spacing: -0.02em; margin: 4px 0; }
.faixa { position: relative; height: 28px; margin: 20px 0 6px; }
.trilho { position: absolute; top: 12px; left: 0; right: 0; height: 4px; border-radius: 2px; background: var(--linha); }
.banda { position: absolute; top: 8px; height: 12px; border-radius: 6px; background: #6da7ec; }
.ponto { position: absolute; top: 4px; width: 20px; height: 20px; margin-left: -10px; border-radius: 50%;
  background: var(--pulso-escuro); border: 3px solid var(--superficie); }
.escala { display: flex; justify-content: space-between; font-size: 12px; color: var(--mudo); }
.linha-selo { display: flex; gap: 12px; align-items: center; margin: 18px 0 8px; }
.pergunta h3 { font-size: 17px; margin: 10px 0; } .pergunta .seg { margin-top: 20px; }
.ganho { font-size: 14px; color: var(--tinta-2); margin: 20px 0; padding: 12px; border-radius: 8px;
  background: var(--pagina); border: 1px solid var(--linha); }
"""
    return pagina("Wireframe — primeira estimativa", corpo, 1440, css)


def wf_diagnostico():
    ind = R["indicadores"]["EMP-C"]
    conf = R["confiabilidade"]["EMP-C"]
    part = ind["IND-04_participacao"]
    nomes = {"COMBUSTIVEL": "Combustível", "MANUTENCAO": "Manutenção", "PEDAGIO": "Pedágio", "SEGURO": "Seguro",
             "TRIBUTO": "Tributos", "OUTROS": "Outros", "MULTA": "Multas"}
    barras = "".join(f'<div class="bl"><span>{nomes[k]}</span><div class="bt"><div class="bb" '
                     f'style="width:{100 * v / max(part.values()):.1f}%"></div></div><span class="tab">{pct(v)}</span></div>'
                     for k, v in sorted(part.items(), key=lambda x: -x[1]))
    pri = R["oportunidades"]["EMP-C"]["priorizacao"]
    resp = {"OP-C1": "Manutenção", "OP-C2": "Gestor de frota", "OP-C3": "Gestor de frota", "OP-C4": "Jurídico",
            "OP-C5": "Gestor de frota", "OP-C6": "Financeiro"}
    linhas = ""
    for p in pri[:5]:
        liq = mil(p["liquida_base"]) if p["estagio"] != "hipotese" else "só no cenário otimista"
        linhas += (f'<tr><td><strong>{p["titulo"]}</strong><br><span class="mudo">{p["id"]}</span></td>'
                   f'<td>{estagio_html(p["estagio"])}</td><td><span class="selo">{ICONE[p["confianca"]]} {p["confianca"]}</span></td>'
                   f'<td class="num">{liq}</td><td>{resp[p["id"]]}</td></tr>')
    serie = R["consumo_EMP-C"]["series"]["C-V07"]["razao_pares"]
    vals = list(serie.values())
    pts = " ".join(f"{i * 300 / (len(vals) - 1):.1f},{(1.05 - v) / 0.3 * 70:.1f}" for i, v in enumerate(vals))
    exc = {x["veiculo_id"]: x for x in R["consumo_EMP-C"]["excesso"]}
    corpo = f"""
<div class="aviso">Wireframe conceitual · dados sintéticos · não é interface implementada</div>
<header class="topo"><div class="marca">{PULSO.format(w=34, h=20, cor="#2a78d6")}<span>frota <b>pulse</b></span></div>
  <nav class="sec">Visão geral · <strong>Diagnóstico</strong> · Plano de ação · Dados</nav>
  <span class="sec">Empresa Sintética C (fictícia) · jul/2025 a jun/2026</span></header>
<main>
  <section class="kpis">
    <div class="cartao"><p class="rotulo">Custo total (12 meses)</p><p class="valor">{mi(ind['IND-01_custo_total_brl'])}</p></div>
    <div class="cartao"><p class="rotulo">Custo por km</p><p class="valor">R$ {dec(ind['IND-03_custo_por_km_brl'])}</p>
      <p class="mudo pequeno">cobertura de km {pct(ind['IND-03_cobertura_km'], 0)}</p></div>
    <div class="cartao"><p class="rotulo">Custo por veículo·mês</p><p class="valor">{mil(ind['IND-02_custo_por_veiculo_mes_brl'])}</p></div>
    <div class="cartao"><p class="rotulo">Confiabilidade do diagnóstico</p>
      <p class="selo grande">{ICONE[conf['selo']]} {conf['selo']}</p>
      <p class="mudo pequeno">pior dimensão: {dec(conf['minimo'], 1)} de 100</p></div>
  </section>
  <section class="duas">
    <div class="cartao"><h3>Onde está o custo</h3><p class="mudo pequeno">participação por categoria (competência)</p>{barras}</div>
    <div class="cartao proximo">
      <p class="rotulo">Próximo passo recomendado</p>
      <h3>Inspecionar C-V07, C-V15 e C-V22</h3>
      <p class="sec">Rendimento caiu desde jan/2026: C-V07 de {dec(exc['C-V07']['km_l_base'])} para
        {dec(exc['C-V07']['km_l_recente'])} km/L. Excesso estimado no semestre:
        {mil(sum(x['custo_excesso_h1'] for x in exc.values()))}.</p>
      <svg width="300" height="78" viewBox="0 -4 300 78" aria-label="razão km/L de C-V07 em relação aos pares">
        <line x1="0" x2="300" y1="{(1.05 - 1.0) / 0.3 * 70:.1f}" y2="{(1.05 - 1.0) / 0.3 * 70:.1f}" stroke="#c3c2b7"/>
        <polyline points="{pts}" fill="none" stroke="#2a78d6" stroke-width="2" stroke-linejoin="round"/></svg>
      <p class="mudo pequeno">razão km/L do veículo ÷ mediana dos pares, jul/25 a jun/26</p>
      <p class="sec pequeno">Responsável: manutenção · revisar em 30 dias · confiança moderada (causa a confirmar)</p>
      <span class="botao">Iniciar ação</span> <span class="botao sec">Ver registros de origem</span>
    </div>
  </section>
  <section class="cartao">
    <h3>Achados e oportunidades</h3>
    <p class="mudo pequeno">economia líquida anual no cenário-base; hipóteses não entram no cenário-base</p>
    <table><thead><tr><th>Oportunidade</th><th>Estágio de evidência</th><th>Confiança</th>
      <th class="num">Economia líquida/ano</th><th>Responsável</th></tr></thead><tbody>{linhas}</tbody></table>
  </section>
</main>"""
    css = """
body { height: 1180px; padding-top: 30px; }
.topo { display: flex; justify-content: space-between; align-items: center; padding: 18px 32px;
  border-bottom: 1px solid var(--linha); background: var(--superficie); }
main { padding: 24px 32px; display: flex; flex-direction: column; gap: 20px; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.kpis p { margin: 4px 0; } .grande { font-size: 20px; } .pequeno { font-size: 12px; }
.duas { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.bl { display: grid; grid-template-columns: 110px 1fr 56px; gap: 12px; align-items: center; margin: 10px 0;
  font-size: 14px; }
.bt { height: 14px; } .bb { height: 14px; background: var(--pulso); border-radius: 0 4px 4px 0; }
.bl .tab { text-align: right; color: var(--tinta-2); }
.proximo { border-color: var(--pulso); }
.proximo h3 { font-size: 22px; margin: 6px 0; }
"""
    return pagina("Wireframe — diagnóstico do gestor", corpo, 1440, css)


def wf_relatorio():
    ind = R["indicadores"]["EMP-C"]
    conf = R["confiabilidade"]["EMP-C"]
    cen = R["oportunidades"]["EMP-C"]["cenarios"]
    pri = [p for p in R["oportunidades"]["EMP-C"]["priorizacao"] if p["estagio"] != "hipotese"][:3]
    hip = [p for p in R["oportunidades"]["EMP-C"]["priorizacao"] if p["estagio"] == "hipotese"]
    linhas = "".join(f'<tr><td>{i + 1}</td><td>{p["titulo"]}</td><td>{NOME_ESTAGIO[p["estagio"]]}</td>'
                     f'<td class="num">{mil(p["liquida_base"])}</td><td>{p["confianca"]}</td></tr>'
                     for i, p in enumerate(pri))
    def payback(c):
        return f"{c['payback_meses']:.1f} mês".replace(".", ",") if c["payback_meses"] else "n/a"
    cen_l = "".join(f'<tr><td>{n.capitalize()}</td><td class="num">{mil(c["economia_liquida_anual"])}</td>'
                    f'<td class="num">{mil(c["implantacao"])}</td><td class="num">{payback(c)}</td>'
                    f'<td class="num">{pct(c["roi_12m"], 0)}</td></tr>' for n, c in cen.items())
    corpo = f"""
<div class="aviso">Wireframe conceitual · dados sintéticos · não é relatório real</div>
<div class="folha">
<header><div class="marca">{PULSO.format(w=34, h=20, cor="#2a78d6")}<span>frota <b>pulse</b></span></div>
  <div class="dir mudo">Relatório executivo · versão da metodologia 0.1</div></header>
<h1>Custos da frota e oportunidades</h1>
<p class="sec">Empresa Sintética C (fictícia) · jul/2025 a jun/2026 · 40 veículos ·
  <span class="selo">{ICONE[conf['selo']]} Confiança {conf['selo'].lower()}</span></p>
<section class="kpis">
  <div><p class="rotulo">Custo total</p><p class="valor">{mi(ind['IND-01_custo_total_brl'])}</p></div>
  <div><p class="rotulo">Custo por km</p><p class="valor">R$ {dec(ind['IND-03_custo_por_km_brl'])}</p></div>
  <div><p class="rotulo">Economia líquida/ano (base)</p><p class="valor">{mil(cen['base']['economia_liquida_anual'])}</p></div>
  <div><p class="rotulo">Recuperação pontual</p><p class="valor">{mil(cen['base']['recuperacao_pontual'])}</p></div>
</section>
<h2>Principais oportunidades</h2>
<table><thead><tr><th>#</th><th>Oportunidade</th><th>Estágio</th><th class="num">Líquida/ano (base)</th><th>Confiança</th></tr></thead>
<tbody>{linhas}</tbody></table>
<h2>Cenários</h2>
<table><thead><tr><th>Cenário</th><th class="num">Economia líquida/ano</th><th class="num">Implantação</th>
<th class="num">Payback</th><th class="num">ROI 12 meses</th></tr></thead><tbody>{cen_l}</tbody></table>
<p class="nota">Conservador: só oportunidades validadas. Base: inclui anomalias com evidência estatística. Otimista:
inclui hipóteses. Fora do cenário-base: {hip[0]['id']}, {hip[0]['titulo']} ({mil(hip[0]['bruta_anual'])} brutos por ano),
que depende de validação contratual e jurídica.</p>
<h2>Premissas e limites</h2>
<ul><li>Fatores de captura e custos de ação são hipóteses de simulação, não promessa de economia.</li>
<li>Custos recorrentes incluem o custo de operar o plano de ação.</li>
<li>Economia realizada será medida contra linha de base ajustada após cada ação.</li></ul>
<footer class="mudo">Gerado a partir do diagnóstico DIAG-EMP-C-2026-07 · trilha de cálculo disponível no painel</footer>
</div>"""
    css = """
body { height: 1200px; padding-top: 30px; }
.folha { width: 1000px; margin: 30px auto; background: var(--superficie); border: 1px solid var(--linha);
  border-radius: 6px; padding: 48px 56px; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 36px; }
h1 { font-size: 34px; } h2 { font-size: 18px; margin: 32px 0 8px; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 28px; padding: 20px 0;
  border-top: 1px solid var(--linha); border-bottom: 1px solid var(--linha); }
.kpis p { margin: 2px 0; } .valor { font-size: 26px; }
.nota { font-size: 13px; color: var(--tinta-2); }
ul { color: var(--tinta-2); font-size: 14px; padding-left: 18px; }
footer { margin-top: 36px; font-size: 12px; }
"""
    return pagina("Wireframe — relatório executivo", corpo, 1100, css)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    arquivos = {"capa.html": capa(), "wf-01-primeira-estimativa.html": wf_estimativa(),
                "wf-02-diagnostico-gestor.html": wf_diagnostico(), "wf-03-relatorio-executivo.html": wf_relatorio()}
    for nome, html in arquivos.items():
        (SAIDA / nome).write_text(html, encoding="utf-8")
    print("ok:", ", ".join(arquivos))


if __name__ == "__main__":
    main()

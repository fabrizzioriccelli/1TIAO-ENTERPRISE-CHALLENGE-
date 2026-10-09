#!/usr/bin/env python3
"""Gera os slides de apoio do vídeo da Sprint 1 (assets/fontes/slides.html), com números do JSON de resultados.

O PDF docs/video/slides-apoio.pdf é a impressão desta página por um navegador sem interface (comando no
README de assets/). Os gráficos e o diagrama de arquitetura são os mesmos arquivos SVG usados na documentação.

Uso:
    python src/gerar_slides.py
"""
from __future__ import annotations

import csv
from collections import Counter

from gerar_visuais import PULSO, R, RAIZ, SAIDA, brl, mi, mil

REPO = "github.com/fabrizzioriccelli/1TIAO-ENTERPRISE-CHALLENGE-"


def slide(n, titulo, corpo, classe=""):
    cab = (f'<header><div class="marca">{PULSO.format(w=34, h=20, cor="#2a78d6")}<span>frota <b>pulse</b></span>'
           f'</div><span class="mudo">Sprint 1 · {n} / 10</span></header>') if n > 1 else ""
    tit = f"<h2>{titulo}</h2>" if titulo else ""
    return f'<section class="slide {classe}">{cab}{tit}{corpo}</section>'


def s01():
    return slide(1, "", f"""
<div class="capa-s">
  <div class="marca grande">{PULSO.format(w=64, h=38, cor="#2a78d6")}<span>frota <b>pulse</b></span></div>
  <h1>Inteligência de custos que transforma dados em decisões</h1>
  <p class="sub">Calculadora de Redução de Custos de Frota<br>Enterprise Challenge FIAP e Sem Parar Empresas · Sprint 1</p>
  <p class="grupo">Grupo: <span class="pend">[nome do grupo e integrantes a preencher]</span></p>
  <p class="nota">Conceito acadêmico com dados sintéticos. Não é produto oficial da Sem Parar Empresas, da Corpay nem da FIAP.</p>
</div>""", "capa")


def s02():
    probs = [("P1", "Dados fragmentados", "Combustível, pedágio, oficina, multas e impostos em fontes e formatos diferentes"),
             ("P2", "Custo absoluto não mede eficiência", "Sem R$/km e km/L, frotas e veículos não são comparáveis"),
             ("P3", "Custo alto nem sempre é desperdício", "Volume, preço e consumo precisam ser separados"),
             ("P4", "Diagnóstico sem ação", "Achado sem próximo passo e sem valor em R$ não muda a gestão"),
             ("P5", "Dados incompletos no primeiro uso", "O gestor quase nunca tem todos os documentos à mão")]
    itens = "".join(f'<li><span class="cod">{c}</span><div><strong>{t}</strong><p>{d}</p></div></li>'
                    for c, t, d in probs)
    return slide(2, "O problema", f"""
<blockquote>"O gestor sabe quanto gastou — mas não onde está perdendo. Combustível, manutenção, pedágio, multas e
impostos vivem em sistemas separados. A gestão é reativa e o custo real nunca aparece consolidado."
<cite>Briefing Sem Parar Empresas</cite></blockquote>
<ol class="lista">{itens}</ol>""")


def s03():
    visoes = [("Gestor de frota", 10, "US-GF-01 a 10"), ("CFO e liderança", 4, "US-CF-01 a 04"),
              ("Sem Parar Empresas", 6, "US-SP-01 a 06")]
    cols = "".join(f'<div class="cartao"><div class="valor">{q}</div><div class="rotulo">{v}</div>'
                   f'<div class="mudo pq">{ids}</div></div>' for v, q, ids in visoes)
    destaques = [("US-GF-09", "Sempre ter uma estimativa, mesmo com poucos dados"),
                 ("US-GF-10", "Receber perguntas sobre o que informar a seguir"),
                 ("US-GF-06", "Ver a economia estimada em reais"),
                 ("US-SP-06", "Oportunidades comerciais, com base legal e preferência registrada (LGPD)")]
    lis = "".join(f'<li><span class="cod">{c}</span>{t}</li>' for c, t in destaques)
    return slide(3, "20 User Stories oficiais, todas rastreadas", f"""
<div class="tres">{cols}</div>
<div class="duas">
  <div><h3>Prioridade (MoSCoW)</h3>
    <table class="tab"><tr><td>Must</td><td class="num">14</td></tr><tr><td>Should</td><td class="num">4</td></tr>
    <tr><td>Could</td><td class="num">2</td></tr><tr><td>Won't</td><td class="num">0</td></tr></table>
    <p class="mudo pq">Matriz com funcionalidade, critério de aceite, dependência e Sprint prevista.</p></div>
  <div><h3>As quatro que definem o produto</h3><ul class="lista-s">{lis}</ul></div>
</div>""")


def s04():
    caps = [("01", "Entender", "Documentos em qualquer formato, com origem e status de cada valor"),
            ("02", "Diagnosticar", "Custo total, indicadores normalizados e desvios com evidência"),
            ("03", "Comparar", "Histórico, pares e referências, só quando há equivalência"),
            ("04", "Otimizar", "Ações com economia em R$ por cenário e um próximo passo"),
            ("05", "Acompanhar", "Atualização mensal e economia realizada medida")]
    itens = "".join(f'<div class="cartao cap"><span class="cod">{n}</span><strong>{t}</strong><p>{d}</p></div>'
                    for n, t, d in caps)
    princ = [("Simples", "3 perguntas para a primeira estimativa"), ("Confiável", "origem de cada valor e selo de confiança"),
             ("Flexível", "aceita CSV, planilha, PDF, foto e resposta"), ("Progressivo", "a faixa estreita a cada dado")]
    p = "".join(f"<li><strong>{a}</strong>: {b}</li>" for a, b in princ)
    return slide(4, "Visão do produto: cinco capacidades", f"""
<div class="cinco">{itens}</div>
<div class="duas">
  <div><h3>Diferencial</h3><p class="grande-t">Dizer quanto se pode confiar em cada número: toda estimativa aparece como
  faixa provável, com a parcela que vem de documento e um selo de confiança.</p></div>
  <div><h3>Princípios do briefing</h3><ul class="lista-s">{p}</ul></div>
</div>""")


def s05():
    linhas = {}
    for t in ("veiculos", "despesas"):
        with open(RAIZ / "data" / "sintetico" / f"{t}.csv", encoding="utf-8") as f:
            linhas[t] = list(csv.DictReader(f))
    veic = Counter("EMP-" + r["veiculo_id"][0] for r in linhas["veiculos"])
    with open(RAIZ / "data" / "sintetico" / "gabarito_cenarios.csv", encoding="utf-8") as f:
        tipos = Counter(r["tipo"] for r in csv.DictReader(f))
    ind = R["indicadores"]
    meses = {"EMP-A": 6, "EMP-B": 12, "EMP-C": 12}

    def custo(v):
        return mil(v, 0) if v < 1e6 else mi(v)
    frotas = "".join(
        f'<tr><td>{e}</td><td class="num">{veic[e]}</td><td class="num">{meses[e]}</td>'
        f'<td class="num">{custo(ind[e]["IND-01_custo_total_brl"])}</td></tr>'
        for e in ("EMP-A", "EMP-B", "EMP-C"))
    nomes = {"problema_dado": "Problemas de dado", "lacuna": "Lacunas", "achado_negocio": "Achados de negócio",
             "justificavel": "Custos altos justificáveis", "controle_negativo": "Controles negativos"}
    cen = "".join(f'<tr><td>{nomes[k]}</td><td class="num">{v}</td></tr>' for k, v in tipos.items())
    return slide(5, "Dados: nenhum valor sem origem", f"""
<div class="tres-l">
  <div class="cartao modelo">
    <div class="no">Arquivo de origem<span>formato, hash, recebimento</span></div>
    <div class="seta">↓</div>
    <div class="no forte">Despesa<span>valor, competência, categoria, linha de origem</span></div>
    <div class="seta">↓</div>
    <div class="no">Status do valor<span>observado · corrigido · imputado · estimado · não disponível</span></div>
    <p class="mudo pq">181 campos documentados no dicionário, com tipo, unidade, validação e sensibilidade.</p>
  </div>
  <div><h3>Três frotas fictícias</h3>
    <table class="tab"><tr><th>Empresa</th><th class="num">Veículos</th><th class="num">Meses</th><th class="num">Custo</th></tr>{frotas}</table>
    <p class="mudo pq">{f"{len(linhas['despesas']):,}".replace(",", ".")} despesas sintéticas, semente fixa e reprodutível.</p></div>
  <div><h3>34 cenários planejados</h3>
    <table class="tab">{cen}</table>
    <p class="aviso-t">As regras detectaram 100% dos erros injetados, mas foram escritas conhecendo os erros:
    isso prova a mecânica, não o desempenho com dados reais.</p></div>
</div>""")


def s06():
    est = R["estimativa_EMP-A"]
    n0, n3 = est["niveis"]["0"], est["niveis"]["3"]
    return slide(6, "Estimativa progressiva: a faixa estreita a cada dado", f"""
<div class="grafico"><img src="../graficos/estimativa-progressiva.svg" alt="Faixas de estimativa por nível"></div>
<div class="tres">
  <div class="cartao"><div class="rotulo">Só com a composição da frota (N0)</div>
    <div class="valor pq-v">{mil(n0["p10"], 0)} a {mil(n0["p90"], 0)}</div></div>
  <div class="cartao"><div class="rotulo">Próxima pergunta sugerida</div>
    <div class="valor pq-v">Enviar a apólice de seguro</div><div class="mudo pq">maior redução de incerteza por esforço</div></div>
  <div class="cartao"><div class="rotulo">Último nível (N3)</div>
    <div class="valor pq-v">Valor real fora da faixa</div><div class="mudo pq">mostrado de propósito; calibração testada
    em 280 ensaios</div></div>
</div>""")


def s07():
    return slide(7, "Custo alto não é desperdício", """
<div class="duas g">
  <div class="grafico"><img src="../graficos/decomposicao-lmdi.svg" alt="Decomposição LMDI do custo de combustível"></div>
  <div class="lado">
    <h3>Decomposição em quilômetros, consumo e preço</h3>
    <p>C-V01 custa mais porque roda mais: o efeito atividade explica o aumento e o consumo é melhor que o dos pares.</p>
    <p>C-V07 piorou o consumo de 2,34 para 2,02 km/L: o efeito intensidade explica a diferença.</p>
    <h3>Detecção de queda (CUSUM)</h3>
    <p>3 de 3 quedas injetadas detectadas em 1 a 2 meses, sem alarme falso entre os 40 veículos da EMP-C.</p>
  </div>
</div>""")


def s08():
    c = R["oportunidades"]["EMP-C"]["cenarios"]
    b = R["oportunidades"]["EMP-B"]["cenarios"]
    return slide(8, "Economia líquida em três cenários", f"""
<div class="duas g">
  <div class="grafico"><img src="../graficos/cenarios-economia.svg" alt="Economia líquida anual por cenário"></div>
  <div class="lado">
    <h3>Escada de evidência</h3>
    <p>Os cenários diferem pelo nível de evidência que incluem, não por percentuais arbitrários. O resultado já desconta
    implantação, custos recorrentes e o custo de executar o plano.</p>
    <div class="cartao"><div class="rotulo">EMP-C, cenário-base</div><div class="valor">{mil(c["base"]["economia_liquida_anual"], 0)} por ano</div></div>
    <div class="cartao"><div class="rotulo">EMP-B, cenário-base</div><div class="valor">{brl(b["base"]["economia_liquida_anual"])} por ano</div>
    <div class="mudo pq">o custo de executar supera a economia; a calculadora não inventa resultado</div></div>
  </div>
</div>""")


def s09():
    return slide(9, "Arquitetura", """
<div class="duas g">
  <div class="grafico"><img src="../diagramas/arquitetura-geral.svg" alt="Arquitetura geral"></div>
  <div class="lado">
    <ul class="lista-s">
      <li><strong>Monólito modular</strong> em Python com FastAPI</li>
      <li><strong>PostgreSQL</strong> com isolamento por cliente</li>
      <li><strong>Processo separado</strong> para ler documentos</li>
      <li><strong>Cálculos determinísticos</strong> e versionados</li>
      <li><strong>IA lê e explica, não calcula</strong> valores financeiros</li>
      <li><strong>LGPD</strong>: finalidade, consentimento e auditoria</li>
    </ul>
  </div>
</div>""")


def s10():
    etapas = [("Sprint 1", "Especificação", "esta entrega"), ("Sprint 2", "Ingestão e primeira estimativa", ""),
              ("Sprint 3", "Diagnóstico, benchmark e recomendações", ""), ("Sprint 4", "Produto testado com gestores", "")]
    itens = "".join(f'<li class="{"atual" if i == 0 else ""}"><span class="cod">{s}</span><strong>{t}</strong>'
                    f'<span class="mudo">{x}</span></li>' for i, (s, t, x) in enumerate(etapas))
    return slide(10, "Próximos passos", f"""
<ol class="linha-tempo">{itens}</ol>
<p class="mudo pq">Quantidade de Sprints é hipótese de planejamento até a confirmação do calendário oficial.</p>
<div class="cartao repo"><div class="rotulo">Documentação completa no repositório</div><div class="valor pq-v">{REPO}</div></div>
""")


CSS = """
@page { size: 1920px 1080px; margin: 0; }
body { width: 1920px; }
.slide { width: 1920px; height: 1080px; padding: 64px 96px; position: relative; overflow: hidden; page-break-after: always;
  background: var(--pagina); display: flex; flex-direction: column; gap: 32px; }
header { display: flex; justify-content: space-between; align-items: center; font-size: 22px; }
header .marca { font-size: 26px; }
h2 { font-size: 66px; line-height: 1.1; }
h3 { font-size: 34px; margin-bottom: 18px; }
p, li, td, th { font-size: 31px; }
.pq { font-size: 25px; } .pq-v { font-size: 38px !important; }
.cod { font-family: var(--fonte-titulo); font-weight: 600; color: var(--pulso-escuro); margin-right: 14px; }
.cartao { padding: 26px 30px; }
.valor { font-size: 58px; } .rotulo { font-size: 25px; margin-bottom: 8px; }
.tres, .tres-l { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }
.tres-l { grid-template-columns: 1.1fr 1fr 1fr; align-items: start; }
.duas { display: grid; grid-template-columns: 1fr 1fr; gap: 56px; align-items: start; }
.duas.g { grid-template-columns: 1.35fr 1fr; flex: 1; min-height: 0; align-items: stretch; }
.tab .num { white-space: nowrap; }
.cinco { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }
.cap strong { display: block; font-size: 34px; margin-top: 10px; } .cap p { font-size: 25px; color: var(--tinta-2); margin: 8px 0 0; }
.grafico { background: var(--superficie); border: 1px solid var(--linha); border-radius: var(--raio); padding: 20px;
  display: flex; align-items: center; justify-content: center; min-height: 0; flex: 1; }
.grafico img { width: 100%; height: 100%; object-fit: contain; }
.lado { align-self: start; }
.lado p { color: var(--tinta-2); margin: 0 0 18px; } .lado h3 { margin-top: 8px; } .lado .cartao { margin-top: 16px; }
blockquote { margin: 0; font-family: var(--fonte-titulo); font-size: 42px; line-height: 1.3; border-left: 4px solid var(--pulso);
  padding-left: 32px; max-width: 1500px; }
cite { display: block; font-family: var(--fonte); font-style: normal; font-size: 25px; color: var(--mudo); margin-top: 14px; }
.lista { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 34px 64px; }
.lista li { display: flex; } .lista strong { font-size: 34px; } .lista p { margin: 6px 0 0; font-size: 27px; color: var(--tinta-2); }
.lista-s { list-style: none; padding: 0; margin: 0; color: var(--tinta); }
.lista-s li { padding: 16px 0; border-bottom: 1px solid var(--linha); }
.grande-t { font-size: 38px; line-height: 1.4; }
.tab td, .tab th { font-size: 28px; padding: 12px 10px; }
.modelo { display: flex; flex-direction: column; align-items: stretch; gap: 6px; }
.no { border: 1px solid var(--eixo); border-radius: 8px; padding: 12px 16px; font-weight: 600; font-size: 28px; }
.no span { display: block; font-weight: 400; font-size: 23px; color: var(--tinta-2); }
.no.forte { border: 2px solid var(--pulso); }
.seta { text-align: center; color: var(--mudo); font-size: 28px; }
.aviso-t { font-size: 25px; color: var(--tinta-2); border-left: 3px solid var(--serio); padding-left: 14px; }
.linha-tempo { list-style: none; padding: 0; margin: 40px 0 0; display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.linha-tempo li { border-top: 4px solid var(--linha); padding-top: 22px; display: flex; flex-direction: column; gap: 8px; }
.linha-tempo li.atual { border-top-color: var(--pulso); }
.linha-tempo strong { font-size: 40px; line-height: 1.2; }
.repo { margin-top: auto; }
.capa-s { margin: auto 0; display: flex; flex-direction: column; gap: 28px; }
.marca.grande { font-size: 56px; }
.capa-s h1 { font-size: 104px; line-height: 1.05; max-width: 1400px; }
.sub { font-size: 38px; color: var(--tinta-2); margin: 0; }
.grupo { font-size: 32px; margin: 0; } .pend { color: var(--critico); }
.capa-s .nota { font-size: 24px; color: var(--mudo); margin-top: 40px; }
"""


def main():
    corpo = "".join(f() for f in (s01, s02, s03, s04, s05, s06, s07, s08, s09, s10))
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Frota Pulse — slides de apoio</title><link rel="stylesheet" href="estilo.css"><style>{CSS}</style></head>
<body>{corpo}</body></html>
"""
    (SAIDA / "slides.html").write_text(html, encoding="utf-8")
    print("ok: slides.html")


if __name__ == "__main__":
    main()

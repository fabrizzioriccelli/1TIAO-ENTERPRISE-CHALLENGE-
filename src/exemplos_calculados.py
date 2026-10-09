#!/usr/bin/env python3
"""Calcula os exemplos numéricos citados na documentação a partir da massa sintética.

Saídas:
    data/resultados/exemplos-calculados.json      todos os valores, sem arredondamento de exibição
    data/resultados/diagnostico-exemplo-EMP-C.json estrutura de um diagnóstico com rastreabilidade
    docs/anexos/exemplos-calculados.md             tabelas em português, geradas automaticamente

Uso:
    python src/exemplos_calculados.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import calculos as C

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "data" / "sintetico"
SAIDA = RAIZ / "data" / "resultados"
ANEXO = RAIZ / "docs" / "anexos" / "exemplos-calculados.md"
H2_2025 = [str(p) for p in pd.period_range("2025-07", "2025-12", freq="M")]
H1_2026 = [str(p) for p in pd.period_range("2026-01", "2026-06", freq="M")]

# Hipóteses de ação usadas nas oportunidades (não observadas; ver docs/economia-recomendacoes.md)
HIP = {
    "diagnostico_mecanico_por_veiculo": 1_500.0,
    "politica_abastecimento_implantacao": 2_000.0,
    "monitoramento_preco_anual": 4_800.0,
    "rotina_conferencia_eixos_implantacao": 1_000.0,
    "plano_preventivo_por_veiculo_implantacao": 2_000.0,
    "preventiva_adicional_mensal_por_veiculo": 300.0,
    "custo_programa_anual": {"EMP-B": 12_000.0, "EMP-C": 30_000.0},
}


# ----------------------------------------------------------------------------- formatação pt-BR
def brl(x: float, casas: int = 2) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/d"
    s = f"{abs(x):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {s}" if x < 0 else f"R$ {s}"


def num(x: float, casas: int = 0) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/d"
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x: float, casas: int = 1) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/d"
    return f"{100 * x:.{casas}f}%".replace(".", ",")


def tabela(cab: list[str], linhas: list[list]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    out += ["| " + " | ".join(str(c) for c in l) + " |" for l in linhas]
    return "\n".join(out)


def jsonavel(o):
    if isinstance(o, dict):
        return {str(k): jsonavel(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonavel(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and np.isnan(o):
        return None
    return o


# ----------------------------------------------------------------------------- cálculos
def main():
    b = C.carregar(DADOS)
    data_ref = b.meta["data_referencia_analise"]
    R: dict = {"data_referencia_analise": data_ref, "hipoteses_de_acao": HIP}

    # 1. Qualidade
    problemas = C.validar(b)
    aval = C.avaliar_regras(b, problemas)
    base = C.base_analitica(b, problemas)
    R["qualidade"] = {
        "marcacoes_por_regra": problemas.groupby("regra_id").despesa_id.nunique().to_dict(),
        "avaliacao": aval.to_dict("records"),
        "marcacoes_fora_do_gabarito": aval.attrs["marcacoes_fora_do_gabarito"],
        "valor_excluido_duplicidade": {e: float(base[(base.empresa_id == e) & base.excluida].valor_brl.sum())
                                       for e in ["EMP-A", "EMP-B", "EMP-C"]},
        "valor_em_quarentena": {e: float(base[(base.empresa_id == e) & base.quarentena].valor_brl.abs().sum())
                                for e in ["EMP-A", "EMP-B", "EMP-C"]},
    }

    # 2. Indicadores básicos
    paineis = {e: C.montar_painel(b, base, e) for e in ["EMP-A", "EMP-B", "EMP-C"]}
    R["indicadores"] = {e: C.indicadores_basicos(p) for e, p in paineis.items()}
    fuel_b = R["qualidade"]["valor_excluido_duplicidade"]["EMP-B"]
    R["efeito_deduplicacao_EMP-B"] = {
        "duplicado_excluido": fuel_b,
        "combustivel_valido": float(paineis["EMP-B"].custo_total_categoria["COMBUSTIVEL"]),
        "inflacao_que_seria_reportada": fuel_b / float(paineis["EMP-B"].custo_total_categoria["COMBUSTIVEL"])}

    # 3. Caixa x competência (EMP-B)
    db = base[(base.empresa_id == "EMP-B") & base.custo_valido]
    caixa = db.assign(m=db.data_evento.str[:7]).groupby("m").valor_brl.sum().reindex(paineis["EMP-B"].meses).fillna(0)
    comp = paineis["EMP-B"].custo_mes_veiculo.groupby("competencia").valor.sum().reindex(paineis["EMP-B"].meses)
    R["caixa_vs_competencia_EMP-B"] = {"caixa": caixa.to_dict(), "competencia": comp.to_dict()}

    # 4. Consumo, CUSUM e decomposição (EMP-C)
    cons = C.consumo_mensal(b, base, "EMP-C")
    bl = cons[cons.competencia.isin(H2_2025)].copy()
    bl["dev"] = bl.razao_pares - bl.groupby("veiculo_id").razao_pares.transform("mean")
    sigma = bl.groupby("categoria_id").dev.std(ddof=1)
    C.CUSUM_H = 5.0
    alarmes, series = {}, {}
    for vid, g in cons.groupby("veiculo_id"):
        serie = g.set_index("competencia").razao_pares.sort_index()
        s, al = C.cusum_queda(serie, 6, float(sigma[g.categoria_id.iloc[0]]))
        if al:
            alarmes[vid] = al
        if vid in ("C-V07", "C-V15", "C-V22", "C-V05"):
            series[vid] = {"razao_pares": serie.round(4).to_dict(), "cusum": s.round(2).to_dict()}
    base_ratio = cons[cons.competencia.isin(H2_2025)].groupby("veiculo_id").razao_pares.median()
    exc = []
    for vid in alarmes:
        g = cons[(cons.veiculo_id == vid) & cons.competencia.isin(H1_2026)].copy()
        g["rend_esperado"] = base_ratio[vid] * g.km_l_pares
        g["litros_excesso"] = (g.litros - g.km / g.rend_esperado).clip(lower=0)
        g["custo_excesso"] = g.litros_excesso * g.preco_medio
        exc.append({"veiculo_id": vid, "alarme": alarmes[vid], "km_l_base": float(
            cons[(cons.veiculo_id == vid) & cons.competencia.isin(H2_2025)].km_l.median()),
                    "km_l_recente": float(g.km.sum() / g.litros.sum()), "litros_excesso_h1": float(g.litros_excesso.sum()),
                    "custo_excesso_h1": float(g.custo_excesso.sum())})
    R["consumo_EMP-C"] = {"sigma_intra_veiculo": sigma.to_dict(), "cusum_k": C.CUSUM_K, "cusum_h": C.CUSUM_H,
                          "alarmes": alarmes, "excesso": exc, "series": series}

    def lmdi_temporal(vid):
        g = cons[cons.veiculo_id == vid]
        def tot(meses):
            x = g[g.competencia.isin(meses)]
            return float(x.km.sum()), float(x.litros.sum()), float(x.custo.sum())
        a0, l0, c0 = tot(H2_2025)
        a1, l1, c1 = tot(H1_2026)
        r = C.lmdi(c1, a1, l1 / a1, c1 / l1, a0, l0 / a0, c0 / l0)
        r.update({"veiculo_id": vid, "km_0": a0, "km_1": a1, "km_l_0": a0 / l0, "km_l_1": a1 / l1,
                  "preco_0": c0 / l0, "preco_1": c1 / l1})
        return r

    R["lmdi"] = {
        "temporal_C-V07": lmdi_temporal("C-V07"),
        "temporal_C-V01": lmdi_temporal("C-V01"),
        "pares_C-V01": C.decompor_combustivel(cons, "C-V01", H1_2026),
        "pares_C-V03": C.decompor_combustivel(cons, "C-V03", H1_2026),
        "pares_C-V07": C.decompor_combustivel(cons, "C-V07", H1_2026),
    }

    # 5. Preço pago acima da referência interna (EMP-B e EMP-C)
    for e in ["EMP-B", "EMP-C"]:
        por_v = C.premio_preco(b, base, e)
        R[f"preco_{e}"] = {"premio_total": float(por_v.premio.sum()),
                           "veiculos_z_acima_limiar": por_v[por_v.z > C.ZMOD_LIMIAR].sort_values(
                               "premio", ascending=False).round(4).reset_index().to_dict("records"),
                           "top8": por_v.sort_values("premio", ascending=False).head(8).round(4).reset_index().to_dict("records")}

    # 6. Manutenção e utilização (EMP-B)
    mb = b.manutencoes.merge(base[["despesa_id", "empresa_id", "veiculo_id", "valor_brl", "data_evento", "custo_valido"]],
                             on="despesa_id")
    mb = mb[(mb.empresa_id == "EMP-B") & mb.custo_valido & mb.data_evento.str[:7].isin(paineis["EMP-B"].meses)]
    km_b = b.uso_veiculo_mensal[b.uso_veiculo_mensal.competencia.isin(paineis["EMP-B"].meses)].groupby(
        "veiculo_id").km_rodados.sum()
    vb = b.veiculos[b.veiculos.frota_id == "FRO-B1"].set_index("veiculo_id")
    piv = mb.pivot_table(index="veiculo_id", columns="tipo", values="valor_brl", aggfunc="sum").fillna(0.0)
    piv = piv.reindex(vb.index).fillna(0.0)
    piv["km"] = km_b
    piv["categoria"] = vb.categoria_id
    piv["ano"] = vb.ano_fabricacao
    piv["pct_corretiva"] = piv.corretiva / (piv.corretiva + piv.preventiva)
    piv["corretiva_por_km"] = piv.corretiva / piv.km
    toco = piv[piv.categoria == "CAM_TOCO"]
    antigos = toco[toco.ano <= 2014]
    novos = toco[toco.ano > 2014]
    ref_km = float(novos.corretiva_por_km.median())
    excesso = ((antigos.corretiva_por_km - ref_km).clip(lower=0) * antigos.km).sum()
    R["manutencao_EMP-B"] = {
        "toco_antigos": antigos[["ano", "km", "corretiva", "preventiva", "pct_corretiva", "corretiva_por_km"]].round(4).reset_index().to_dict("records"),
        "toco_novos_mediana_corretiva_por_km": ref_km,
        "toco_novos_mediana_pct_corretiva": float(novos.pct_corretiva.median()),
        "excesso_corretiva_antigos": float(excesso),
    }
    uso_b = b.uso_veiculo_mensal[b.uso_veiculo_mensal.veiculo_id.isin(vb.index)
                                 & b.uso_veiculo_mensal.competencia.isin(paineis["EMP-B"].meses)]
    kmvm = uso_b.groupby("veiculo_id").km_rodados.mean().to_frame("km_mes")
    kmvm["categoria"] = vb.categoria_id
    kmvm["mediana_pares"] = kmvm.groupby("categoria").km_mes.transform("median")
    kmvm["razao"] = kmvm.km_mes / kmvm.mediana_pares
    sub = kmvm[kmvm.razao < C.SUBUTILIZACAO_LIMIAR]
    # custos fixos por competência dos subutilizados: IPVA e licenciamento próprios + seguro rateado pelo valor
    rat_b = C.ratear_competencia(base[(base.empresa_id == "EMP-B") & base.custo_valido])
    rat_b = rat_b[rat_b.competencia.isin(paineis["EMP-B"].meses)]
    seguro_b = float(rat_b[rat_b.categoria_custo == "SEGURO"].valor_competencia.sum())
    fixos = {}
    for vid in sub.index:
        trib = float(rat_b[(rat_b.veiculo_id == vid) & (rat_b.categoria_custo == "TRIBUTO")].valor_competencia.sum())
        seg = seguro_b * vb.loc[vid, "valor_referencia_brl"] / vb.valor_referencia_brl.sum()
        fixos[vid] = {"km_mes": float(sub.loc[vid, "km_mes"]), "razao_pares": float(sub.loc[vid, "razao"]),
                      "tributos": trib, "seguro_rateado": seg, "fixo_anual": trib + seg}
    R["utilizacao_EMP-B"] = {"limiar": C.SUBUTILIZACAO_LIMIAR, "subutilizados": fixos,
                             "mediana_pares_util": float(kmvm[kmvm.categoria == "UTIL_LEVE"].km_mes.median())}

    # 7. Multas
    mul = b.multas.merge(base[["despesa_id", "empresa_id", "veiculo_id", "valor_brl", "data_evento", "custo_valido"]],
                         on="despesa_id")
    R["multas"] = {}
    for e in ["EMP-B", "EMP-C"]:
        x = mul[(mul.empresa_id == e) & mul.custo_valido & mul.data_evento.str[:7].isin(paineis[e].meses)]
        orig = x[x.tipo_multa == "original"]
        km = R["indicadores"][e]["km_observado"]
        R["multas"][e] = {
            "qtd_original": int(len(orig)), "qtd_nic": int((x.tipo_multa == "nic").sum()),
            "valor_nic": float(x[x.tipo_multa == "nic"].valor_brl.sum()),
            "qtd_sem_desconto": int((orig.desconto_aplicado == 0).sum()),
            "desconto_perdido": float((orig[orig.desconto_aplicado == 0].valor_original * 0.20).sum()),
            "por_10mil_km": len(orig) / km * 10_000, "valor_total": float(x.valor_brl.sum())}

    # 8. Pedágio (EMP-B duplicidade; EMP-C eixos suspensos, Vale-Pedágio e lacunas)
    dup_ids = problemas.loc[problemas.regra_id == "R-PED-DUP", "despesa_id"]
    R["pedagio_EMP-B"] = {"duplicadas_qtd": int(len(dup_ids)),
                          "duplicadas_valor": float(base[base.despesa_id.isin(dup_ids)].valor_brl.sum()),
                          "custo_por_km": float(paineis["EMP-B"].custo_total_categoria["PEDAGIO"]) / R["indicadores"]["EMP-B"]["km_observado"]}
    pc = b.pedagios.merge(base[["despesa_id", "empresa_id", "veiculo_id", "valor_brl", "natureza_custo", "custo_valido",
                                "data_evento"]], on="despesa_id")
    pc = pc[pc.empresa_id == "EMP-C"].merge(b.viagens, on=["viagem_id", "veiculo_id"], how="left")
    pc = pc.merge(b.veiculos[["veiculo_id", "categoria_id"]], on="veiculo_id").merge(
        b.categorias_veiculo[["categoria_id", "eixos"]], on="categoria_id")
    pc["eixos_devidos"] = pc.eixos - pc.eixos_suspensos_declarados.fillna(0)
    ind = pc[(pc.tipo_viagem == "retorno_vazio") & (pc.eixos_cobrados > pc.eixos_devidos)]
    sobre = (ind.valor_brl * (1 - ind.eixos_devidos / ind.eixos_cobrados)).sum()
    vpo = pc[(pc.tipo_viagem == "carregada_lotacao") & (pc.vale_pedagio_recebido == False)  # noqa: E712
             & (pc.natureza_custo == "proprio")]
    # lacunas: tarifa média por km das viagens com tag, aplicada às viagens sem registro de pedágio
    tag = pc[(pc.meio_pagamento == "tag") & pc.custo_valido]
    taxa = (tag.groupby(["categoria_id", tag.tipo_viagem == "retorno_vazio"]).valor_brl.sum()
            / tag.groupby(["categoria_id", tag.tipo_viagem == "retorno_vazio"]).km_percorrido.sum())
    vg = b.viagens.merge(b.veiculos[["veiculo_id", "categoria_id", "possui_tag_pedagio"]], on="veiculo_id")
    vg = vg[vg.veiculo_id.str.startswith("C-")]
    sem_registro = vg[~vg.viagem_id.isin(b.pedagios.viagem_id.dropna())
                      & ~((vg.tipo_viagem == "carregada_lotacao") & (vg.vale_pedagio_recebido == True))]  # noqa: E712
    sem_registro = sem_registro.assign(taxa=[taxa.get((c, t == "retorno_vazio"), np.nan) for c, t in
                                             zip(sem_registro.categoria_id, sem_registro.tipo_viagem)])
    sem_registro["estimado"] = sem_registro.km_percorrido * sem_registro.taxa
    fev = sem_registro[(sem_registro.data_inicio.str[:7] == "2026-02") & sem_registro.possui_tag_pedagio]
    manual = sem_registro[~sem_registro.possui_tag_pedagio]
    R["pedagio_EMP-C"] = {
        "eixo_suspenso_qtd": int(len(ind)), "eixo_suspenso_sobrecobranca": float(sobre),
        "vpo_qtd_viagens": int(len(vpo)), "vpo_valor_proprio": float(vpo.valor_brl.sum()),
        "custeado_terceiros": float(pc[pc.natureza_custo == "custeado_terceiro"].valor_brl.sum()),
        "taxa_por_km": {f"{k[0]}|{'vazio' if k[1] else 'carregado'}": float(v) for k, v in taxa.items()},
        "lacuna_fev_estimada": float(fev.estimado.sum()), "lacuna_fev_real": b.lacunas["G21"],
        "lacuna_manual_estimada": float(manual.estimado.sum()), "lacuna_manual_real": b.lacunas["G22"],
        "viagens_manual_sem_comprovante": int(len(manual)),
        "custo_por_km_proprio": float(paineis["EMP-C"].custo_total_categoria["PEDAGIO"]) / R["indicadores"]["EMP-C"]["km_observado"],
    }

    # 9. Estimativa progressiva (EMP-A)
    est = C.estimativa_progressiva(b, base)
    R["estimativa_EMP-A"] = est
    obs_a = est["niveis"][2]["parcela_observada"] * est["niveis"][2]["p50"]
    lacuna_a = est["niveis"][2]["p50"] - obs_a

    # 9b. Calibração da faixa de manutenção (backtest com meses mascarados)
    cal = C.calibrar_manutencao(b, base, "EMP-B", "UTIL_LEVE", H2_2025)
    R["backtest_manutencao"] = {
        "todas_as_janelas_priori_generica": C.backtest_manutencao(b, base),
        "janelas_2026_priori_generica": C.backtest_manutencao(b, base, inicio_minimo=6, n_subconjuntos=120),
        "janelas_2026_calibrada_jul_dez_2025": C.backtest_manutencao(b, base, inicio_minimo=6, n_subconjuntos=120,
                                                                      parametros=cal),
        "parametros_calibrados": cal,
        "priori_generica": {"eventos_por_10mil_km": C.PRIORI["manut_eventos_por_10mil_km"]["UTIL_LEVE"],
                            "severidade_mediana": C.PRIORI["manut_severidade_mediana"]["UTIL_LEVE"],
                            "severidade_sigma": C.PRIORI["manut_severidade_sigma"]},
    }

    # 10. Confiabilidade
    lac_c = R["pedagio_EMP-C"]["lacuna_fev_estimada"] + R["pedagio_EMP-C"]["lacuna_manual_estimada"]
    R["confiabilidade"] = {
        "EMP-A": C.confiabilidade(b, base, problemas, "EMP-A", lacuna_a, data_ref),
        "EMP-B": C.confiabilidade(b, base, problemas, "EMP-B", 0.0, data_ref),
        "EMP-C": C.confiabilidade(b, base, problemas, "EMP-C", lac_c, data_ref),
    }

    # 11. Oportunidades, priorização e cenários
    nic_b, nic_c = R["multas"]["EMP-B"], R["multas"]["EMP-C"]
    exc_total = sum(x["custo_excesso_h1"] for x in exc)
    ops_c = [
        C.Oportunidade("OP-C1", "EMP-C", f"Queda de rendimento em {len(exc)} cavalos mecânicos", "anomalia",
                       2 * exc_total, (0.4, 0.6, 0.8), HIP["diagnostico_mecanico_por_veiculo"] * len(exc), 0.0,
                       "Moderada", 1.0, 1.5, evidencias={"veiculos": list(alarmes), "metodo": "CUSUM + LMDI"}),
        C.Oportunidade("OP-C2", "EMP-C", "Abastecimento acima da referência de preço da própria frota",
                       "oportunidade_validada", R["preco_EMP-C"]["premio_total"], (0.3, 0.5, 0.7),
                       HIP["politica_abastecimento_implantacao"], HIP["monitoramento_preco_anual"], "Alta", 1.0, 2.0),
        C.Oportunidade("OP-C3", "EMP-C", "Cobrança de eixo suspenso em retornos vazios", "oportunidade_validada",
                       float(sobre), (0.5, 0.7, 0.9), HIP["rotina_conferencia_eixos_implantacao"], 0.0, "Moderada",
                       1.25, 1.0, recuperacao_pontual=float(sobre)),
        C.Oportunidade("OP-C4", "EMP-C", "Viagens de lotação sem registro de Vale-Pedágio", "hipotese",
                       float(vpo.valor_brl.sum()), (0.0, 0.3, 0.6), 0.0, 0.0, "Baixa", 1.0, 2.0, risco="medio"),
        C.Oportunidade("OP-C5", "EMP-C", "Multas NIC (não indicação do condutor)", "oportunidade_validada",
                       nic_c["valor_nic"], (0.7, 0.9, 1.0), 0.0, 0.0, "Alta", 1.25, 0.5),
        C.Oportunidade("OP-C6", "EMP-C", "Multas pagas sem o desconto de 20%", "oportunidade_validada",
                       nic_c["desconto_perdido"], (0.5, 0.8, 1.0), 0.0, 0.0, "Alta", 1.0, 0.25),
    ]
    fixo_sub = sum(v["fixo_anual"] for v in fixos.values())
    n_ant = len(antigos)
    ops_b = [
        C.Oportunidade("OP-B1", "EMP-B", "Multas NIC (não indicação do condutor)", "oportunidade_validada",
                       nic_b["valor_nic"], (0.7, 0.9, 1.0), 0.0, 0.0, "Alta", 1.25, 0.5),
        C.Oportunidade("OP-B2", "EMP-B", "Multas pagas sem o desconto de 20%", "oportunidade_validada",
                       nic_b["desconto_perdido"], (0.5, 0.8, 1.0), 0.0, 0.0, "Alta", 1.0, 0.25),
        C.Oportunidade("OP-B3", "EMP-B", "Passagens de pedágio cobradas em duplicidade", "oportunidade_validada",
                       R["pedagio_EMP-B"]["duplicadas_valor"], (0.5, 0.8, 1.0), 0.0, 0.0, "Alta", 1.25, 0.5,
                       recuperacao_pontual=R["pedagio_EMP-B"]["duplicadas_valor"]),
        C.Oportunidade("OP-B4", "EMP-B", f"Custos fixos de {len(fixos)} utilitários subutilizados", "hipotese",
                       fixo_sub, (0.0, 1 / 3, 2 / 3), 0.0, 0.0, "Baixa", 1.0, 2.0, risco="medio"),
        C.Oportunidade("OP-B6", "EMP-B", "Abastecimento acima da referência de preço da própria frota",
                       "oportunidade_validada", R["preco_EMP-B"]["premio_total"], (0.3, 0.5, 0.7),
                       HIP["politica_abastecimento_implantacao"], 0.0, "Alta", 1.0, 1.0),
        C.Oportunidade("OP-B5", "EMP-B", f"Manutenção corretiva elevada em {n_ant} caminhões de 2012-2013",
                       "hipotese", float(excesso), (0.20, 0.35, 0.50),
                       HIP["plano_preventivo_por_veiculo_implantacao"] * n_ant,
                       HIP["preventiva_adicional_mensal_por_veiculo"] * 12 * n_ant, "Moderada", 1.0, 3.0),
    ]
    R["oportunidades"] = {}
    for e, ops in (("EMP-B", ops_b), ("EMP-C", ops_c)):
        pri = C.priorizar(ops)
        R["oportunidades"][e] = {"lista": [jsonavel(o.__dict__) for o in ops], "priorizacao": pri.to_dict("records"),
                                 "cenarios": C.cenarios_portfolio(ops, HIP["custo_programa_anual"][e]),
                                 "proximo_passo": pri.iloc[0][["id", "titulo"]].to_dict()}
    R["combinacao_alavancas"] = C.combinar_alavancas(200_000.0, [0.06, 0.04])
    # Sensibilidade do cenário-base da EMP-C: captura 20% menor e custos de ação dobrados
    sens = {}
    for nome, f_cap, f_custo in (("referencia", 1.0, 1.0), ("captura_-20%", 0.8, 1.0),
                                 ("custos_x2", 1.0, 2.0), ("captura_-20%_e_custos_x2", 0.8, 2.0)):
        ajust = [C.Oportunidade(**{**o.__dict__, "captura": tuple(c * f_cap for c in o.captura),
                                   "implantacao": o.implantacao * f_custo,
                                   "recorrente_anual": o.recorrente_anual * f_custo}) for o in ops_c]
        cen = C.cenarios_portfolio(ajust, HIP["custo_programa_anual"]["EMP-C"] * f_custo)["base"]
        sens[nome] = {k: cen[k] for k in ("economia_liquida_anual", "implantacao", "custos_recorrentes",
                                          "payback_meses", "roi_12m")}
    R["sensibilidade_EMP-C_base"] = sens

    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "exemplos-calculados.json").write_text(json.dumps(jsonavel(R), ensure_ascii=False, indent=1) + "\n",
                                                     encoding="utf-8")
    diagnostico_exemplo(b, base, problemas, R, alarmes)
    ANEXO.parent.mkdir(parents=True, exist_ok=True)
    ANEXO.write_text(anexo(R), encoding="utf-8")
    print("ok:", SAIDA / "exemplos-calculados.json", ANEXO)


def diagnostico_exemplo(b, base, problemas, R, alarmes):
    """Estrutura de saída de um diagnóstico com rastreabilidade (achado -> registros -> documentos)."""
    d = base[base.empresa_id == "EMP-C"]
    def amostra(mascara, n=5):
        x = d[mascara].head(n)
        return [{"despesa_id": r.despesa_id, "origem_id": r.origem_id, "referencia_na_origem": r.referencia_na_origem}
                for r in x.itertuples()]
    veics = list(alarmes)
    pri = {p["id"]: p for p in R["oportunidades"]["EMP-C"]["priorizacao"]}
    achados = [
        {"achado_id": "ACH-C-01", "estagio": "anomalia", "indicador": "IND-07", "regra": "REC-05",
         "titulo": "Queda persistente de rendimento (km/L) em relação aos pares",
         "metodo": "CUSUM unilateral sobre razão km/L do veículo / mediana dos pares (k=0,5; h=5)",
         "evidencias": R["consumo_EMP-C"]["excesso"], "oportunidade_id": "OP-C1",
         "registros_amostra": amostra(d.veiculo_id.isin(veics) & (d.categoria_custo == "COMBUSTIVEL")
                                      & d.data_evento.str[:7].isin(H1_2026)),
         "proxima_acao": "Inspeção mecânica dirigida (injeção, filtros, pneus) e conversa com o condutor; "
                         "revalidar o indicador após 30 dias."},
        {"achado_id": "ACH-C-02", "estagio": "oportunidade_validada", "indicador": "IND-08", "regra": "REC-04",
         "titulo": "Preço pago acima da mediana mensal da frota (+2% de tolerância)",
         "evidencias": {"premio_total": R["preco_EMP-C"]["premio_total"],
                        "veiculos_destaque": [x["veiculo_id"] for x in R["preco_EMP-C"]["veiculos_z_acima_limiar"]]},
         "oportunidade_id": "OP-C2", "registros_amostra": amostra(d.categoria_custo == "COMBUSTIVEL"),
         "proxima_acao": "Definir postos preferenciais por rota e regra de bloqueio/alerta acima da referência."},
        {"achado_id": "ACH-C-03", "estagio": "oportunidade_validada", "indicador": "IND-10", "regra": "REC-08",
         "titulo": "Eixo suspenso cobrado em retorno vazio",
         "evidencias": {"viagens": R["pedagio_EMP-C"]["eixo_suspenso_qtd"],
                        "sobrecobranca": R["pedagio_EMP-C"]["eixo_suspenso_sobrecobranca"]},
         "oportunidade_id": "OP-C3", "registros_amostra": amostra(d.categoria_custo == "PEDAGIO"),
         "proxima_acao": "Contestar as cobranças dentro do prazo do emissor e conferir a declaração de eixos."},
    ]
    saida = {
        "aviso": "Exemplo gerado a partir de dados SINTÉTICOS para ilustrar a estrutura de saída. Não é resultado real.",
        "diagnostico_id": "DIAG-EMP-C-2026-07", "empresa_id": "EMP-C",
        "periodo": b.meta["periodos"]["EMP-C"], "data_referencia": b.meta["data_referencia_analise"],
        "versao_metodologia": "0.1 (Sprint 1, especificação)",
        "confiabilidade": R["confiabilidade"]["EMP-C"],
        "indicadores": {k: v for k, v in R["indicadores"]["EMP-C"].items() if not k.startswith("IND-05")},
        "achados": achados,
        "priorizacao": [pri[k] for k in pri],
        "cenarios": R["oportunidades"]["EMP-C"]["cenarios"],
        "proximo_passo": R["oportunidades"]["EMP-C"]["proximo_passo"],
        "premissas": {"fatores_de_captura": "hipóteses de simulação por cenário (conservador, base, otimista)",
                      "hipoteses_de_acao": HIP, "anualizacao": "OP-C1 anualizada a partir de jan-jun/2026 (x2), "
                                                                "supondo persistência do desvio"},
    }
    (SAIDA / "diagnostico-exemplo-EMP-C.json").write_text(json.dumps(jsonavel(saida), ensure_ascii=False, indent=1)
                                                          + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- anexo
def anexo(R: dict) -> str:
    L = ["# Anexo — exemplos calculados", "",
         "> Gerado automaticamente por `src/exemplos_calculados.py` a partir de `data/sintetico/` (dados **fictícios**).",
         "> Não edite à mão: rode o script novamente. Os números servem para verificar fórmulas e regras; não "
         "descrevem nenhuma frota real e não são promessa de economia.", "",
         f"Data de referência da análise: **{R['data_referencia_analise']}**.", ""]
    # Qualidade
    L += ["## 1. Regras de qualidade aplicadas aos cenários injetados", "",
          "Cobertura = registros injetados detectados pela regra esperada. Nos controles negativos, 100% significa "
          "que nenhum registro legítimo foi marcado.", ""]
    L.append(tabela(["Cenário", "Regra(s)", "Injetados", "Detectados", "Cobertura"],
                    [[a["cenario_id"], a["regras"], a["injetados"], a["detectados"], pct(a["cobertura"], 0)]
                     for a in R["qualidade"]["avaliacao"]]))
    fora = R["qualidade"]["marcacoes_fora_do_gabarito"]
    L += ["", f"Marcações fora do gabarito: **{sum(fora.values()) if fora else 0}**. "
          "Limitação: as regras foram escritas conhecendo os erros injetados; este teste comprova a mecânica, "
          "não o desempenho em dados reais.", ""]
    q = R["qualidade"]
    L.append(tabela(["Empresa", "Excluído por duplicidade", "Em quarentena"],
                    [[e, brl(q["valor_excluido_duplicidade"][e]), brl(q["valor_em_quarentena"][e])]
                     for e in ["EMP-A", "EMP-B", "EMP-C"]]))
    ed = R["efeito_deduplicacao_EMP-B"]
    L += ["", f"Sem a regra R-DUP-ARQ, o combustível da EMP-B apareceria {pct(ed['inflacao_que_seria_reportada'])} "
          f"maior ({brl(ed['duplicado_excluido'])}), um desvio inexistente.", ""]
    # Indicadores
    L += ["## 2. Indicadores básicos (custo por competência, dentro da janela de cada empresa)", ""]
    linhas = []
    for e, ind in R["indicadores"].items():
        linhas.append([e, brl(ind["IND-01_custo_total_brl"]), ind["veiculos_mes"],
                       brl(ind["IND-02_custo_por_veiculo_mes_brl"]), brl(ind["IND-03_custo_por_km_brl"], 3),
                       pct(ind["IND-03_cobertura_km"]), num(ind["km_observado"])])
    L.append(tabela(["Empresa", "IND-01 Custo total", "Veículos·mês", "IND-02 R$/veículo·mês", "IND-03 R$/km",
                     "Cobertura de km", "km observados"], linhas))
    L += ["", "Participação por categoria (IND-04):", ""]
    cats = C.CATEGORIAS_CUSTO
    L.append(tabela(["Empresa"] + cats, [[e] + [pct(R["indicadores"][e]["IND-04_participacao"].get(c, 0)) for c in cats]
                                          for e in R["indicadores"]]))
    cx = R["caixa_vs_competencia_EMP-B"]
    L += ["", "### Caixa x competência (EMP-B)", "",
          "A renovação do seguro paga à vista em abr/2026 cria um pico de caixa que não é aumento de custo.", ""]
    L.append(tabela(["Mês", "Caixa", "Competência"], [[m, brl(cx["caixa"][m]), brl(cx["competencia"][m])]
                                                       for m in cx["caixa"]]))
    # Consumo
    co = R["consumo_EMP-C"]
    L += ["", "## 3. Rendimento e mudança persistente (EMP-C)", "",
          f"Desvio-padrão intra-veículo da razão km/L ÷ mediana dos pares na linha de base (jul-dez/2025): "
          f"{', '.join(f'{k} {num(v, 4)}' for k, v in co['sigma_intra_veiculo'].items())}. "
          f"CUSUM com k = {num(co['cusum_k'], 1)} e h = {num(co['cusum_h'], 1)}.", ""]
    L.append(tabela(["Veículo", "Alarme", "km/L base", "km/L jan-jun/26", "Litros em excesso", "Custo em excesso"],
                    [[x["veiculo_id"], x["alarme"], num(x["km_l_base"], 2), num(x["km_l_recente"], 2),
                      num(x["litros_excesso_h1"]), brl(x["custo_excesso_h1"])] for x in co["excesso"]]))
    L += ["", "### Decomposição LMDI do custo de combustível", "",
          "C = km × (L/km) × (R$/L). Os três efeitos somam exatamente a diferença (resíduo zero).", ""]
    lm = R["lmdi"]
    linhas = []
    for k, r in lm.items():
        linhas.append([k.replace("_", " "), brl(r["custo_veiculo"]), brl(r["custo_referencia"]), brl(r["diferenca"]),
                       brl(r["atividade"]), brl(r["intensidade"]), brl(r["preco"]), brl(r["residuo"])])
    L.append(tabela(["Comparação", "Custo", "Referência", "Diferença", "Atividade (km)", "Intensidade (L/km)",
                     "Preço (R$/L)", "Resíduo"], linhas))
    pr = R["preco_EMP-C"]
    L += ["", "### Preço pago acima da referência interna (EMP-C)", "",
          f"Prêmio total pago acima da mediana mensal da frota (+2%): **{brl(pr['premio_total'])}** em 12 meses "
          f"(EMP-B: {brl(R['preco_EMP-B']['premio_total'])}).", ""]
    L.append(tabela(["Veículo", "Prêmio", "R$/L de prêmio", "% abastecimentos acima", "z modificado"],
                    [[x["veiculo_id"], brl(x["premio"]), num(x["premio_por_litro"], 4), pct(x["pct_acima"]),
                      num(x["z"], 2)] for x in pr["top8"]]))
    # Manutenção e utilização
    mb = R["manutencao_EMP-B"]
    L += ["", "## 4. Manutenção e utilização (EMP-B)", "",
          f"Mediana de corretiva por km dos caminhões toco 2017-2022: {brl(mb['toco_novos_mediana_corretiva_por_km'], 4)}/km "
          f"({pct(mb['toco_novos_mediana_pct_corretiva'])} do gasto preventivo+corretivo).", ""]
    L.append(tabela(["Veículo", "Ano", "km", "Corretiva", "Preventiva", "% corretiva", "Corretiva/km"],
                    [[x["veiculo_id"], x["ano"], num(x["km"]), brl(x["corretiva"]), brl(x["preventiva"]),
                      pct(x["pct_corretiva"]), brl(x["corretiva_por_km"], 4)] for x in mb["toco_antigos"]]))
    L += ["", f"Excesso de corretiva dos quatro caminhões antigos em relação à mediana: **{brl(mb['excesso_corretiva_antigos'])}**.", ""]
    ut = R["utilizacao_EMP-B"]
    L.append(tabela(["Veículo", "km/mês", "Razão vs pares", "Tributos", "Seguro rateado", "Custo fixo anual"],
                    [[k, num(v["km_mes"]), pct(v["razao_pares"]), brl(v["tributos"]), brl(v["seguro_rateado"]),
                      brl(v["fixo_anual"])] for k, v in ut["subutilizados"].items()]))
    L += ["", f"Mediana de km/mês dos utilitários: {num(ut['mediana_pares_util'])} km; limiar de subutilização: "
          f"{pct(ut['limiar'], 0)} da mediana.", ""]
    # Multas e pedágio
    L += ["## 5. Multas e pedágio", ""]
    L.append(tabela(["Empresa", "Multas originais", "Por 10 mil km", "NIC (qtd)", "NIC (valor pago)",
                     "Sem desconto (qtd)", "Desconto perdido"],
                    [[e, m["qtd_original"], num(m["por_10mil_km"], 2), m["qtd_nic"], brl(m["valor_nic"]),
                      m["qtd_sem_desconto"], brl(m["desconto_perdido"])] for e, m in R["multas"].items()]))
    pb, pc = R["pedagio_EMP-B"], R["pedagio_EMP-C"]
    L += ["", f"EMP-B: {pb['duplicadas_qtd']} passagens duplicadas ({brl(pb['duplicadas_valor'])}); pedágio de "
          f"{brl(pb['custo_por_km'], 3)}/km.", "",
          f"EMP-C: {pc['eixo_suspenso_qtd']} retornos vazios com eixo suspenso cobrado (sobrecobrança de "
          f"{brl(pc['eixo_suspenso_sobrecobranca'])}); {pc['vpo_qtd_viagens']} viagens de lotação sem Vale-Pedágio "
          f"com pedágio pago pela transportadora ({brl(pc['vpo_valor_proprio'])}); pedágio custeado por terceiros "
          f"(excluído do custo próprio): {brl(pc['custeado_terceiros'])}.", "",
          "Estimativa de lacunas com dados de contexto (viagens do TMS × tarifa média por km das viagens com tag):", ""]
    L.append(tabela(["Lacuna", "Estimada", "Valor real (gabarito)", "Erro"],
                    [["Extrato de fev/2026 ausente", brl(pc["lacuna_fev_estimada"]), brl(pc["lacuna_fev_real"]),
                      pct(pc["lacuna_fev_estimada"] / pc["lacuna_fev_real"] - 1)],
                     ["Pedágio manual sem comprovante", brl(pc["lacuna_manual_estimada"]), brl(pc["lacuna_manual_real"]),
                      pct(pc["lacuna_manual_estimada"] / pc["lacuna_manual_real"] - 1)]]))
    # Estimativa progressiva
    est = R["estimativa_EMP-A"]
    L += ["", "## 6. Estimativa progressiva (EMP-A, out/2025 a mar/2026)", "",
          f"Valor real do período (observado + lacunas do gabarito): **{brl(est['valor_real_brl'])}**. "
          "Faixa = P10 a P90 de 20.000 simulações (não é probabilidade calibrada).", ""]
    L.append(tabela(["Nível", "Informação disponível", "P10", "P50", "P90", "Largura", "Parcela observada",
                     "Contém o real?"],
                    [[f"N{k}", v["descricao"], brl(v["p10"], 0), brl(v["p50"], 0), brl(v["p90"], 0),
                      brl(v["largura_p10_p90"], 0), pct(v["parcela_observada"], 0),
                      "sim" if v["contem_valor_real"] else "não"] for k, v in est["niveis"].items()]))
    L += ["", "Próximas perguntas no nível N2, ordenadas por redução da faixa por unidade de esforço:", ""]
    L.append(tabela(["Ordem", "Pergunta", "Esforço", "Redução da largura", "Redução %"],
                    [[i + 1, q["pergunta"], q["esforco"], brl(q["reducao_largura_brl"], 0), pct(q["reducao_pct"])]
                     for i, q in enumerate(est["proximas_perguntas"])]))
    dec = est["declaracoes_nivel_1"]
    L += ["", f"Respostas simuladas no N1: km médio declarado {num(dec['km_medio_mensal_declarado'])} km/mês "
          f"(média observada nos veículos com odômetro: {num(dec['km_medio_mensal_real_veiculos_com_odometro'])}); "
          f"combustível declarado {brl(dec['combustivel_mensal_declarado'], 0)}/mês.", ""]
    bt = R["backtest_manutencao"]
    L += ["### Teste de calibração da faixa de manutenção (EMP-B, utilitários)", "",
          "Janelas de 6 meses: 3 meses observados e 3 mascarados; subconjuntos aleatórios de 3 a 8 veículos. "
          "Em uma faixa P10-P90 calibrada, espera-se cobertura perto de 80%, com erros divididos entre as caudas.", ""]
    L.append(tabela(["Ensaio", "Parâmetros", "Ensaios", "Cobertura P10-P90", "Acima do P90", "Abaixo do P10",
                     "Erro mediano do P50"],
                    [["Todas as janelas", "premissa genérica", bt["todas_as_janelas_priori_generica"]["ensaios"],
                      pct(bt["todas_as_janelas_priori_generica"]["cobertura_p10_p90"]),
                      pct(bt["todas_as_janelas_priori_generica"]["fracao_acima_p90"]),
                      pct(bt["todas_as_janelas_priori_generica"]["fracao_abaixo_p10"]),
                      pct(bt["todas_as_janelas_priori_generica"]["erro_mediano_p50"])],
                     ["Janelas de 2026", "premissa genérica", bt["janelas_2026_priori_generica"]["ensaios"],
                      pct(bt["janelas_2026_priori_generica"]["cobertura_p10_p90"]),
                      pct(bt["janelas_2026_priori_generica"]["fracao_acima_p90"]),
                      pct(bt["janelas_2026_priori_generica"]["fracao_abaixo_p10"]),
                      pct(bt["janelas_2026_priori_generica"]["erro_mediano_p50"])],
                     ["Janelas de 2026", "calibrada em jul-dez/2025", bt["janelas_2026_calibrada_jul_dez_2025"]["ensaios"],
                      pct(bt["janelas_2026_calibrada_jul_dez_2025"]["cobertura_p10_p90"]),
                      pct(bt["janelas_2026_calibrada_jul_dez_2025"]["fracao_acima_p90"]),
                      pct(bt["janelas_2026_calibrada_jul_dez_2025"]["fracao_abaixo_p10"]),
                      pct(bt["janelas_2026_calibrada_jul_dez_2025"]["erro_mediano_p50"])]]))
    pc_, pg = bt["parametros_calibrados"], bt["priori_generica"]
    L += ["", f"Premissa genérica: {num(pg['eventos_por_10mil_km'], 2)} eventos por 10 mil km, severidade mediana "
          f"{brl(pg['severidade_mediana'], 0)} (sigma {num(pg['severidade_sigma'], 2)}). Calibrada: "
          f"{num(pc_['eventos_por_10mil_km'], 2)} eventos por 10 mil km, severidade mediana "
          f"{brl(pc_['severidade_mediana'], 0)} (sigma {num(pc_['severidade_sigma'], 2)}), a partir de "
          f"{pc_['eventos']} eventos em {num(pc_['km'])} km.", ""]
    # Confiabilidade
    L += ["## 7. Confiabilidade do diagnóstico", ""]
    dims = ["C_completude", "A_atualidade", "K_consistencia", "R_rastreabilidade", "X_contexto"]
    L.append(tabela(["Empresa"] + ["C", "A", "K", "R", "X", "Mínimo", "Selo"],
                    [[e] + [num(c["dimensoes"][d], 1) for d in dims] + [num(c["minimo"], 1), c["selo"]]
                     for e, c in R["confiabilidade"].items()]))
    L += ["", "Escala 0-100 por dimensão; o selo usa a pior dimensão (elo mais fraco).", ""]
    # Oportunidades
    L += ["## 8. Oportunidades, cenários e priorização", "",
          "Economia líquida anual = economia bruta × fator de captura − custo recorrente. Fatores de captura e "
          "custos de ação são hipóteses (ver `hipoteses_de_acao` no JSON). Cenários: conservador = só oportunidades "
          "validadas; base = + anomalias; otimista = + hipóteses. Os custos recorrentes incluem o custo de operar o "
          "plano (EMP-B R$ 12.000/ano; EMP-C R$ 30.000/ano, hipóteses). Recuperações pontuais (contestação de "
          "cobranças passadas) não entram na economia anual.", ""]
    for e, o in R["oportunidades"].items():
        L += [f"### {e}", ""]
        def cel(p, k, chave):
            return brl(p[chave], 0) if p["estagio"] in C.INCLUSAO_CENARIO[k] else "não entra"
        L.append(tabela(["Ordem", "Id", "Oportunidade", "Estágio", "Bruta anual", "Líquida cons.", "Líquida base",
                         "Líquida otim.", "Confiança", "Esforço (p-sem)", "Prioridade"],
                        [[p["ordem"], p["id"], p["titulo"], p["estagio"].replace("_", " "), brl(p["bruta_anual"], 0),
                          cel(p, 0, "liquida_conservador"), cel(p, 1, "liquida_base"), cel(p, 2, "liquida_otimista"),
                          p["confianca"], num(p["esforco"], 2), num(p["prioridade"], 0)] for p in o["priorizacao"]]))
        L += ["", tabela(["Cenário", "Itens", "Bruta capturada", "Custos recorrentes", "Implantação",
                          "Economia líquida anual", "Payback (meses)", "ROI 12 meses", "Recuperação pontual"],
                         [[k, ", ".join(v["itens"]), brl(v["bruta_capturada"], 0), brl(v["custos_recorrentes"], 0),
                           brl(v["implantacao"], 0), brl(v["economia_liquida_anual"], 0),
                           num(v["payback_meses"], 1) if v["payback_meses"] else "n/a",
                           pct(v["roi_12m"], 0) if v["roi_12m"] is not None else "n/a",
                           brl(v["recuperacao_pontual"], 0)] for k, v in o["cenarios"].items()]),
              "", f"Próximo passo recomendado: **{o['proximo_passo']['id']} — {o['proximo_passo']['titulo']}**.", ""]
    se = R["sensibilidade_EMP-C_base"]
    L += ["### Sensibilidade do cenário-base (EMP-C)", ""]
    L.append(tabela(["Variação", "Economia líquida anual", "Implantação", "Custos recorrentes", "Payback (meses)",
                     "ROI 12 meses"],
                    [[k.replace("_", " "), brl(v["economia_liquida_anual"], 0), brl(v["implantacao"], 0),
                      brl(v["custos_recorrentes"], 0), num(v["payback_meses"], 1) if v["payback_meses"] else "n/a",
                      pct(v["roi_12m"], 0)] for k, v in se.items()]))
    L.append("")
    cb = R["combinacao_alavancas"]
    L += ["### Duas alavancas sobre o mesmo custo", "",
          f"Custo de {brl(cb['custo'], 0)} com reduções de {pct(cb['reducoes'][0], 0)} e {pct(cb['reducoes'][1], 0)}: "
          f"soma ingênua {brl(cb['soma_ingenua'], 0)}; efeito combinado {brl(cb['combinada'], 0)}; "
          f"dupla contagem evitada {brl(cb['dupla_contagem_evitada'], 0)}.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()

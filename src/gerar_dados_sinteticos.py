#!/usr/bin/env python3
"""Gera a massa de dados SINTÉTICOS usada na documentação da Sprint 1 do Frota Pulse.

Este script não faz parte da aplicação. Ele existe para que os exemplos numéricos
da documentação sejam reproduzíveis e verificáveis.

- Todos os valores são fictícios e derivam das hipóteses declaradas em PARAMETROS,
  exportadas para data/parametros-simulacao.csv.
- Nenhum registro corresponde a empresa, veículo, pessoa ou documento real.
  CNPJ e placa não são gerados, para evitar coincidência com registros reais.
- Os problemas de qualidade e as situações operacionais injetados ficam
  registrados no gabarito (gabarito_cenarios.csv e gabarito_registros.csv).

Uso:
    python src/gerar_dados_sinteticos.py
    python src/gerar_dados_sinteticos.py --saida outra/pasta
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEMENTE = 20260710
DATA_REFERENCIA_ANALISE = "2026-07-10"
RAIZ = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# Parâmetros de simulação
# tipo: hipotese_simulacao (escolhido pelo grupo para coerência interna, sem
#       pretensão de representar o mercado), valor_legal (texto legal verificado
#       por busca; ver docs/referencias.md) ou convencao (regra de modelagem).
# --------------------------------------------------------------------------
PARAMETROS: list[dict] = []


def parametro(chave, valor, unidade, tipo, justificativa):
    PARAMETROS.append(
        {"chave": chave, "valor": json.dumps(valor, ensure_ascii=False), "unidade": unidade,
         "tipo": tipo, "fonte_ou_justificativa": justificativa})
    return valor


@dataclass(frozen=True)
class Categoria:
    categoria_id: str
    descricao: str
    combustivel: str
    eixos: int
    tanque_l: float
    classe_peso: str
    rendimento_km_l: tuple[float, float]
    fracao_abastecimento: tuple[float, float]
    valor_novo_brl: tuple[float, float]
    preventiva_intervalo_km: int
    preventiva_custo_brl: tuple[float, float]
    corretiva_eventos_por_10mil_km: float
    corretiva_custo_brl: tuple[float, float]
    pneus_intervalo_km: int
    pneus_custo_brl: tuple[float, float]
    taxa_seguro_anual: tuple[float, float]
    aliquota_ipva: float
    eixos_suspensiveis: int


CATEGORIAS = {c.categoria_id: c for c in [
    Categoria("LEVE_PASSEIO", "Automóvel de passageiros (flex; abastecido com gasolina na simulação)",
              "gasolina", 2, 50, "leve", (10.0, 13.0), (0.55, 0.85), (75_000, 95_000),
              10_000, (450, 800), 0.35, (300, 2_500), 45_000, (1_600, 2_400), (0.040, 0.060), 0.040, 0),
    Categoria("UTIL_LEVE", "Utilitário leve ou furgão (flex; abastecido com gasolina na simulação)",
              "gasolina", 2, 55, "leve", (8.5, 11.0), (0.55, 0.85), (90_000, 130_000),
              10_000, (500, 900), 0.40, (350, 3_000), 45_000, (1_800, 2_800), (0.040, 0.060), 0.020, 0),
    Categoria("VUC", "Veículo urbano de carga", "diesel_s10", 2, 150, "medio", (5.5, 7.0), (0.50, 0.80),
              (230_000, 300_000), 15_000, (900, 1_600), 0.50, (500, 6_000), 60_000, (6_500, 9_500),
              (0.035, 0.050), 0.015, 0),
    Categoria("CAM_TOCO", "Caminhão toco (2 eixos)", "diesel_s10", 2, 275, "medio", (4.0, 5.0), (0.50, 0.80),
              (300_000, 380_000), 20_000, (1_200, 2_200), 0.60, (600, 9_000), 80_000, (8_000, 12_000),
              (0.032, 0.045), 0.015, 0),
    Categoria("CAM_TRUCK", "Caminhão truck (3 eixos)", "diesel_s10", 3, 300, "pesado", (3.0, 3.8), (0.50, 0.80),
              (420_000, 520_000), 20_000, (1_500, 2_600), 0.60, (800, 12_000), 90_000, (12_000, 17_000),
              (0.030, 0.042), 0.015, 1),
    Categoria("CAV_SEMI", "Cavalo mecânico 6x2 com semirreboque (6 eixos no conjunto, tratado como uma unidade de custo)",
              "diesel_s10", 6, 600, "pesado", (2.2, 2.8), (0.55, 0.85), (650_000, 850_000), 25_000, (2_000, 3_500),
              0.70, (1_000, 15_000), 100_000, (22_000, 30_000), (0.030, 0.040), 0.015, 2),
]}
for _c in CATEGORIAS.values():
    parametro(f"categoria.{_c.categoria_id}", {
        "rendimento_km_l": _c.rendimento_km_l, "tanque_l": _c.tanque_l, "valor_novo_brl": _c.valor_novo_brl,
        "preventiva_intervalo_km": _c.preventiva_intervalo_km, "preventiva_custo_brl": _c.preventiva_custo_brl,
        "corretiva_eventos_por_10mil_km": _c.corretiva_eventos_por_10mil_km,
        "corretiva_custo_brl": _c.corretiva_custo_brl, "pneus_intervalo_km": _c.pneus_intervalo_km,
        "pneus_custo_brl": _c.pneus_custo_brl, "taxa_seguro_anual": _c.taxa_seguro_anual,
        "aliquota_ipva": _c.aliquota_ipva}, "várias", "hipotese_simulacao",
        "Ordens de grandeza escolhidas pelo grupo para coerência interna; não são estatísticas de mercado "
        "e devem ser recalibradas com dados reais ou fontes públicas (ex.: ANP para preços).")

PRECO_BASE = parametro("preco_base_combustivel", {"diesel_s10": 6.15, "gasolina": 6.35}, "R$/L",
                       "hipotese_simulacao",
                       "Nível de preço arbitrado para a simulação; não é série da ANP. Calibração prevista com o "
                       "Levantamento de Preços de Combustíveis (ANP) na Sprint 2.")
VARIACAO_MENSAL_PRECO = parametro("variacao_mensal_preco", {
    "2025-07": 1.000, "2025-08": 1.004, "2025-09": 1.010, "2025-10": 1.006, "2025-11": 0.998,
    "2025-12": 0.995, "2026-01": 1.012, "2026-02": 1.020, "2026-03": 1.015, "2026-04": 1.008,
    "2026-05": 1.003, "2026-06": 0.999}, "fator", "hipotese_simulacao",
    "Oscilação moderada para que o efeito preço exista na decomposição; não reproduz o mercado.")
DISPERSAO_POSTO = parametro("dispersao_preco_posto_sigma", 0.02, "log-desvio", "hipotese_simulacao",
                            "Diferença persistente de preço entre postos.")
SOBREPRECO_FORA_REDE = parametro("sobrepreco_postos_fora_da_rede", [0.07, 0.10], "fração",
                                 "hipotese_simulacao", "Usado apenas nos veículos do cenário G13.")
KM_MENSAL = {
    ("urbana_servicos", "LEVE_PASSEIO"): (1_200, 2_200),
    ("urbana_servicos", "UTIL_LEVE"): (1_500, 2_800),
    ("distribuicao_regional", "VUC"): (2_500, 4_000),
    ("distribuicao_regional", "CAM_TOCO"): (3_500, 5_500),
    ("distribuicao_regional", "UTIL_LEVE"): (1_800, 3_000),
    ("rodoviario_longa_distancia", "CAV_SEMI"): (9_000, 13_000),
    ("rodoviario_longa_distancia", "CAM_TRUCK"): (6_000, 9_000),
}
parametro("km_mensal_por_modalidade_categoria", {f"{m}|{c}": v for (m, c), v in KM_MENSAL.items()}, "km/mês",
          "hipotese_simulacao", "Faixa uniforme da quilometragem-base de cada veículo.")
SAZONALIDADE = parametro("sazonalidade_km", {
    "2025-07": 1.00, "2025-08": 1.02, "2025-09": 1.03, "2025-10": 1.04, "2025-11": 1.05, "2025-12": 0.92,
    "2026-01": 0.90, "2026-02": 0.95, "2026-03": 1.00, "2026-04": 0.99, "2026-05": 1.01, "2026-06": 0.98},
    "fator", "hipotese_simulacao", "Oscilação de volume para que variações de custo por volume existam.")
DENSIDADE_PRACAS = parametro("pracas_pedagio_por_100km", {
    "urbana_servicos": 0.25, "distribuicao_regional": 0.70, "rodoviario_longa_distancia": 0.55},
    "praças/100 km", "hipotese_simulacao", "Exposição a rodovias pedagiadas por modalidade.")
TARIFA_BASE = parametro("tarifa_base_praca_categoria_1", [7.5, 18.0], "R$/passagem", "hipotese_simulacao",
                        "Tarifa de veículo leve sorteada uma vez por praça.")
parametro("multiplicador_tarifa", "1 para veículo leve; número de eixos cobrados para veículo comercial",
          "regra", "convencao", "Simplificação da cobrança por eixo; categorias tarifárias reais variam por "
          "concessão.")
MULTA_VALOR = parametro("multa_valor_por_gravidade", {
    "leve": 88.38, "media": 130.16, "grave": 195.23, "gravissima": 293.47}, "R$", "valor_legal",
    "CTB, art. 258 (redação da Lei nº 13.281/2016).")
DIST_GRAVIDADE = parametro("multa_distribuicao_gravidade", {
    "leve": 0.20, "media": 0.45, "grave": 0.25, "gravissima": 0.10}, "probabilidade", "hipotese_simulacao",
    "Composição arbitrada.")
TAXA_MULTAS = parametro("multas_por_veiculo_mes", {"EMP-A": 0.05, "EMP-B": 0.10, "EMP-C": 0.06},
                        "eventos/veículo·mês", "hipotese_simulacao", "Frequência arbitrada.")
parametro("multa_nic_fator", 2, "x multa originária", "valor_legal",
          "CTB, art. 257, § 8º (redação da Lei nº 14.229/2021): pessoa jurídica que não identifica o "
          "condutor no prazo recebe nova multa de 2 vezes a originária.")
PRAZO_INDICACAO = parametro("prazo_indicacao_condutor_dias", 30, "dias", "valor_legal",
                            "CTB, art. 257, § 7º (redação da Lei nº 14.071/2020).")
parametro("desconto_pagamento_ate_vencimento", 0.20, "fração", "valor_legal",
          "CTB, art. 284, caput: pagamento até o vencimento por 80% do valor.")
parametro("desconto_sne", 0.40, "fração", "valor_legal",
          "CTB, art. 284, § 1º: adesão ao sistema de notificação eletrônica sem defesa nem recurso, "
          "pagamento por 60% do valor.")
parametro("isencao_eixo_suspenso", "veículo de carga vazio não paga pedágio sobre eixos suspensos",
          "regra", "valor_legal", "Lei nº 13.103/2015, art. 17 (redação da Lei nº 13.711/2018).")
LICENCIAMENTO = parametro("licenciamento_anual", 160.00, "R$/veículo·ano", "hipotese_simulacao",
                          "Valor arbitrado; varia por UF.")
DEPRECIACAO_ANUAL = parametro("depreciacao_valor_referencia", 0.07, "fração/ano", "hipotese_simulacao",
                              "Usada apenas para o valor de referência de IPVA e seguro.")
parametro("aliquota_ipva", {k: v.aliquota_ipva for k, v in CATEGORIAS.items()}, "fração", "hipotese_simulacao",
          "Alíquotas arbitradas para a simulação; NÃO foram extraídas da legislação estadual.")
LOCACAO_MENSAL = parametro("locacao_mensal_automovel", 3450.00, "R$/veículo·mês", "hipotese_simulacao",
                           "Contrato fictício com manutenção e seguro inclusos.")
TELEMETRIA = parametro("telemetria_mensal", 119.00, "R$/veículo·mês", "hipotese_simulacao",
                       "Serviço de rastreamento fictício.")
FAIXA_PRECO_PLAUSIVEL = parametro("faixa_preco_plausivel", {"diesel_s10": [4.5, 9.0], "gasolina": [4.5, 9.5]},
                                  "R$/L", "convencao", "Regra de validação R-PRECO-FAIXA; revisar a cada "
                                  "trimestre com a série da ANP.")

MESES_PT = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun", 7: "jul", 8: "ago", 9: "set",
            10: "out", 11: "nov", 12: "dez"}


def competencias(inicio: str, fim: str) -> list[str]:
    return [str(p) for p in pd.period_range(inicio, fim, freq="M")]


def dias_do_mes(comp: str) -> int:
    return pd.Period(comp, freq="M").days_in_month


def token(texto: str, prefixo: str, n: int = 8) -> str:
    return f"{prefixo}-{hashlib.sha256(texto.encode()).hexdigest()[:n].upper()}"


class Gerador:
    def __init__(self, semente: int = SEMENTE):
        self.rng = np.random.default_rng(semente)
        self.t: dict[str, list[dict]] = defaultdict(list)
        self.seq: Counter = Counter()
        self.gab_cenarios: list[dict] = []
        self.gab_registros: list[dict] = []
        self.verdade_lacunas: dict[str, float] = defaultdict(float)

    # ---------------- utilidades ----------------
    def u(self, faixa):
        return float(self.rng.uniform(*faixa))

    def proximo(self, prefixo: str, largura: int) -> str:
        self.seq[prefixo] += 1
        return f"{prefixo}-{self.seq[prefixo]:0{largura}d}"

    def data_no_mes(self, comp: str, dia_min: int = 1, dia_max: int | None = None) -> date:
        p = pd.Period(comp, freq="M")
        dia_max = dia_max or p.days_in_month
        return date(p.year, p.month, int(self.rng.integers(dia_min, dia_max + 1)))

    def instante(self, d: date, h0: int = 6, h1: int = 21) -> datetime:
        return datetime(d.year, d.month, d.day, int(self.rng.integers(h0, h1)), int(self.rng.integers(0, 60)))

    def origem(self, emp: str, tipo: str, descricao: str, recebido: datetime, metodo: str,
               confianca: float | None = None, hash_de: str | None = None) -> str:
        oid = self.proximo(f"ORG-{emp[-1]}", 4)
        self.t["origens_dados"].append({
            "origem_id": oid, "empresa_id": emp, "tipo_origem": tipo, "descricao": descricao,
            "hash_sha256": hashlib.sha256((hash_de or f"{emp}|{descricao}").encode()).hexdigest(),
            "data_recebimento": recebido.isoformat(timespec="minutes"), "metodo_extracao": metodo,
            "confianca_extracao_media": None if confianca is None else round(confianca, 3),
            "registros_extraidos": 0})
        return oid

    def despesa(self, emp, frota, veiculo, origem, categoria, subcategoria, data_evento: date, valor: float,
                descricao: str, uf: str, ref: str, comp_ini: str | None = None, comp_fim: str | None = None,
                natureza: str = "proprio", confianca: float | None = None, sub: tuple[str, dict] | None = None):
        did = self.proximo(f"DSP-{emp[-1]}", 6)
        comp = f"{data_evento.year}-{data_evento.month:02d}"
        reg = {
            "despesa_id": did, "empresa_id": emp, "frota_id": frota, "veiculo_id": veiculo, "origem_id": origem,
            "referencia_na_origem": ref, "categoria_custo": categoria, "subcategoria": subcategoria,
            "data_evento": data_evento.isoformat(), "competencia_inicio": comp_ini or comp,
            "competencia_fim": comp_fim or comp, "valor_brl": round(valor, 2), "natureza_custo": natureza,
            "status_valor": "OBSERVADO", "valor_extraido_original": None,
            "confianca_extracao": None if confianca is None else round(confianca, 3),
            "requer_revisao": bool(confianca is not None and confianca < 0.80),
            "descricao_original": descricao, "uf": uf}
        self.t["despesas"].append(reg)
        if sub:
            nome, campos = sub
            self.t[nome].append({"despesa_id": did, **campos})
        return did

    def cenario(self, cid, emp, tipo, classificacao, descricao, regra, registros=(), tabela="despesas",
                valor_real=None, observacao=""):
        registros = list(registros)
        self.gab_cenarios.append({
            "cenario_id": cid, "empresa_id": emp, "tipo": tipo, "classificacao_esperada": classificacao,
            "descricao": descricao, "regra_ou_metodo_esperado": regra, "tabela": tabela,
            "quantidade_registros": len(registros),
            "valor_real_brl": None if valor_real is None else round(valor_real, 2), "observacao": observacao})
        for r in registros:
            self.gab_registros.append({"cenario_id": cid, "tabela": tabela, "registro_id": r})

    def soma(self, ids) -> float:
        alvo = set(ids)
        return round(sum(d["valor_brl"] for d in self.t["despesas"] if d["despesa_id"] in alvo), 2)

    # ---------------- cadastros ----------------
    def cadastrar(self):
        empresas = [
            ("EMP-A", "Empresa Sintética A - Serviços Técnicos (fictícia)", "servicos_tecnicos", "pequena",
             "FRO-A1", "Equipe técnica metropolitana", "urbana_servicos", "2025-10", "2026-03"),
            ("EMP-B", "Empresa Sintética B - Distribuição (fictícia)", "distribuicao", "media",
             "FRO-B1", "Distribuição regional", "distribuicao_regional", "2025-07", "2026-06"),
            ("EMP-C", "Empresa Sintética C - Transporte Rodoviário (fictícia)", "transporte_carga", "grande",
             "FRO-C1", "Rodoviário de longa distância", "rodoviario_longa_distancia", "2025-07", "2026-06"),
        ]
        self.cfg = {}
        for emp, nome, seg, porte, frota, fnome, modal, ini, fim in empresas:
            self.t["empresas"].append({"empresa_id": emp, "razao_social": nome, "segmento": seg,
                                       "porte_frota": porte, "uf_sede": "SP",
                                       "data_cadastro": f"{ini}-01"})
            self.t["frotas"].append({"frota_id": frota, "empresa_id": emp, "nome": fnome,
                                     "modalidade_operacional": modal, "uf_operacao_principal": "SP",
                                     "ativa": True})
            self.cfg[emp] = {"frota": frota, "modal": modal, "comps": competencias(ini, fim)}
        for c in CATEGORIAS.values():
            self.t["categorias_veiculo"].append({
                "categoria_id": c.categoria_id, "descricao": c.descricao, "combustivel_padrao": c.combustivel,
                "eixos": c.eixos, "eixos_suspensiveis": c.eixos_suspensiveis, "capacidade_tanque_l": c.tanque_l,
                "classe_peso": c.classe_peso})

        plano = []  # (emp, categoria, quantidade, faixa_ano, propriedade)
        plano += [("EMP-A", "UTIL_LEVE", 4, (2019, 2022), "propria"),
                  ("EMP-A", "LEVE_PASSEIO", 2, (2020, 2023), "propria"),
                  ("EMP-A", "LEVE_PASSEIO", 2, (2024, 2024), "locada")]
        plano += [("EMP-B", "VUC", 10, (2018, 2023), "propria"),
                  ("EMP-B", "CAM_TOCO", 4, (2012, 2013), "propria"),
                  ("EMP-B", "CAM_TOCO", 8, (2017, 2022), "propria"),
                  ("EMP-B", "UTIL_LEVE", 8, (2019, 2023), "propria")]
        plano += [("EMP-C", "CAV_SEMI", 28, (2016, 2023), "propria"),
                  ("EMP-C", "CAM_TRUCK", 12, (2015, 2022), "propria")]
        self.veiculos: dict[str, dict] = {}
        contador = Counter()
        for emp, cat, qtd, anos, prop in plano:
            for _ in range(qtd):
                contador[emp] += 1
                vid = f"{emp[-1]}-V{contador[emp]:02d}"
                c = CATEGORIAS[cat]
                ano = int(self.rng.integers(anos[0], anos[1] + 1))
                idade = 2026 - ano
                valor_ref = self.u(c.valor_novo_brl) * (1 - DEPRECIACAO_ANUAL) ** idade
                modal = self.cfg[emp]["modal"]
                v = {"veiculo_id": vid, "empresa_id": emp, "frota_id": self.cfg[emp]["frota"],
                     "categoria_id": cat, "ano_fabricacao": ano, "propriedade": prop,
                     "valor_referencia_brl": round(valor_ref, 2),
                     "km_base": self.u(KM_MENSAL[(modal, cat)]), "rend_base": self.u(c.rendimento_km_l),
                     "antigo": ano <= 2014, "flags": set()}
                if v["antigo"]:
                    v["rend_base"] *= 0.95
                v["motoristas"] = [token(f"{vid}|mot{i}", "MOT", 6) for i in range(int(self.rng.integers(1, 3)))]
                self.veiculos[vid] = v
        # Flags de cenário (definidas antes da simulação para manter a coerência dos registros)
        for vid in ["A-V02", "A-V03", "A-V04"]:
            self.veiculos[vid]["flags"].add("sem_odometro")
        for vid in ["B-V28", "B-V29", "B-V30"]:
            self.veiculos[vid]["flags"].add("subutilizado")
            self.veiculos[vid]["km_base"] = self.u((300, 650))
        for vid in ["C-V07", "C-V15", "C-V22"]:
            self.veiculos[vid]["flags"].add("deterioracao")
            self.veiculos[vid]["fator_deterioracao"] = self.u((0.83, 0.88))
        for vid in ["C-V03", "C-V09", "C-V18", "C-V24", "C-V27"]:
            self.veiculos[vid]["flags"].add("fora_rede")
        for vid in ["C-V11", "C-V12", "C-V31", "C-V32"]:
            self.veiculos[vid]["flags"].add("sem_tag")
        for vid in ["C-V01", "C-V02"]:
            self.veiculos[vid]["flags"].add("volume_alto")
            self.veiculos[vid]["km_base"] = 13_000 * 1.25
        for vid, v in self.veiculos.items():
            self.t["veiculos"].append({
                "veiculo_id": vid, "frota_id": v["frota_id"], "categoria_id": v["categoria_id"],
                "placa_token": token(f"placa|{vid}", "PT"), "ano_fabricacao": v["ano_fabricacao"],
                "propriedade": v["propriedade"], "valor_referencia_brl": v["valor_referencia_brl"],
                "data_entrada_frota": f"{max(v['ano_fabricacao'], 2015)}-03-01", "status": "ativo",
                "possui_tag_pedagio": "sem_tag" not in v["flags"]})

        # Postos e praças fictícios
        self.postos = {}
        for emp, n in [("EMP-A", 8), ("EMP-B", 20), ("EMP-C", 50)]:
            postos = []
            for i in range(n):
                fator = float(np.exp(self.rng.normal(0, DISPERSAO_POSTO)))
                rede = emp == "EMP-C" and i < 30
                if rede:
                    fator *= 0.985
                ufs = ["SP", "MG", "GO", "MT", "PR", "MS"] if emp == "EMP-C" else ["SP"]
                postos.append({"codigo": f"POSTO-{emp[-1]}{i + 1:03d}", "fator": fator, "rede": rede,
                               "uf": ufs[i % len(ufs)]})
            self.postos[emp] = postos
        self.postos_fora_rede = [{"codigo": f"POSTO-CX{i + 1:02d}", "fator": 1 + self.u(SOBREPRECO_FORA_REDE),
                                  "rede": False, "uf": ["MT", "GO", "MS"][i % 3]} for i in range(6)]
        self.pracas = {}
        for emp, n in [("EMP-A", 10), ("EMP-B", 25), ("EMP-C", 60)]:
            self.pracas[emp] = [{"codigo": f"PRACA-{emp[-1]}{i + 1:02d}",
                                 "concessionaria": f"CONC-{(i % 7) + 1:02d}", "tarifa": round(self.u(TARIFA_BASE), 2)}
                                for i in range(n)]
        for v in self.veiculos.values():
            emp = v["empresa_id"]
            k = min(6, len(self.pracas[emp]))
            v["rota_pracas"] = list(self.rng.choice(len(self.pracas[emp]), size=k, replace=False))
            v["postos_habituais"] = list(self.rng.choice(len(self.postos[emp]), size=min(5, len(self.postos[emp])),
                                                         replace=False))

    # ---------------- simulação operacional ----------------
    def simular(self):
        self.origens_mensais = {}
        self.km_real = {}
        self.odometro = {vid: int(self.rng.integers(30_000, 400_000)) if not self.veiculos[vid]["antigo"]
                         else int(self.rng.integers(500_000, 800_000)) for vid in self.veiculos}
        self.km_acum = {vid: 0.0 for vid in self.veiculos}
        self.prox_preventiva = {}
        self.prox_pneus = {}
        self.n_preventivas = Counter()
        for vid, v in self.veiculos.items():
            c = CATEGORIAS[v["categoria_id"]]
            self.prox_preventiva[vid] = self.u((0.1, 1.0)) * c.preventiva_intervalo_km
            self.prox_pneus[vid] = self.u((0.2, 1.0)) * c.pneus_intervalo_km
            self.n_preventivas[vid] = int(self.rng.integers(0, 4))
        # B-V05 com revisão completa garantida no período (cenário G08)
        self.n_preventivas["B-V05"] = 3
        self.prox_preventiva["B-V05"] = 5_000
        for emp in ["EMP-A", "EMP-B", "EMP-C"]:
            self.criar_origens_recorrentes(emp)
            for comp in self.cfg[emp]["comps"]:
                for vid, v in self.veiculos.items():
                    if v["empresa_id"] == emp:
                        self.simular_veiculo_mes(v, comp)
        self.simular_tributos_seguros_outros()

    def criar_origens_recorrentes(self, emp):
        o = {}
        for comp in self.cfg[emp]["comps"]:
            p = pd.Period(comp, freq="M")
            receb = datetime(p.year, p.month, p.days_in_month) + timedelta(days=5, hours=10)
            if emp == "EMP-A":
                o[(comp, "comb")] = self.origem(emp, "xlsx", f"extrato_cartao_combustivel_{comp}.xlsx", receb,
                                                "leitura_estruturada")
                o[(comp, "ped")] = self.origem(emp, "pdf_texto", f"extrato_tag_pedagio_{comp}.pdf", receb,
                                               "leitura_estruturada", 0.99)
                o[(comp, "loc")] = self.origem(emp, "pdf_texto", f"fatura_locacao_{comp}.pdf", receb,
                                               "leitura_estruturada", 0.99)
                o[(comp, "txt")] = self.origem(emp, "texto_livre", f"mensagens_estacionamento_{comp}.txt", receb,
                                               "regra_texto", 0.93)
            elif emp == "EMP-B":
                o[(comp, "comb")] = self.origem(emp, "xlsx", f"abastecimentos_{comp}.xlsx", receb,
                                                "leitura_estruturada")
                o[(comp, "ped")] = self.origem(emp, "extrato_pedagio", f"extrato_tag_{comp}.csv", receb,
                                               "leitura_estruturada")
                o[(comp, "man")] = self.origem(emp, "csv", f"erp_manutencao_{comp}.csv", receb,
                                               "leitura_estruturada")
                o[(comp, "txt")] = self.origem(emp, "texto_livre", f"mensagens_lavagem_{comp}.txt", receb,
                                               "regra_texto", 0.91)
            else:
                o[(comp, "comb")] = self.origem(emp, "extrato_cartao_combustivel", f"cartao_combustivel_{comp}.csv",
                                                receb, "leitura_estruturada")
                if comp != "2026-02":  # cenário G21: extrato de fevereiro não enviado
                    o[(comp, "ped")] = self.origem(emp, "extrato_pedagio", f"extrato_tag_{comp}.csv", receb,
                                                   "leitura_estruturada")
                o[(comp, "man")] = self.origem(emp, "pdf_texto", f"notas_oficinas_{comp}.pdf", receb,
                                               "leitura_estruturada", 0.97)
                o[(comp, "tms")] = self.origem(emp, "csv", f"tms_viagens_{comp}.csv", receb, "leitura_estruturada")
                o[(comp, "tel")] = self.origem(emp, "pdf_texto", f"fatura_telemetria_{comp}.pdf", receb,
                                               "leitura_estruturada", 0.99)
                o[(comp, "seg")] = self.origem(emp, "pdf_texto", f"boleto_seguro_frota_{comp}.pdf", receb,
                                               "leitura_estruturada", 0.98)
        self.origens_mensais.update({(emp, *k): val for k, val in o.items()})
        if emp == "EMP-B":
            self.origem_multas_b = self.origem(emp, "xlsx", "controle_multas_2025-07_a_2026-06.xlsx",
                                               datetime(2026, 7, 6, 9), "leitura_estruturada")
        if emp == "EMP-C":
            self.origem_multas_c = self.origem(emp, "xlsx", "multas_frota_2025-2026.xlsx",
                                               datetime(2026, 7, 6, 9), "leitura_estruturada")

    def simular_veiculo_mes(self, v, comp):
        vid, emp = v["veiculo_id"], v["empresa_id"]
        c = CATEGORIAS[v["categoria_id"]]
        frota = v["frota_id"]
        km = v["km_base"] * SAZONALIDADE[comp] * float(np.clip(self.rng.normal(1, 0.08), 0.75, 1.25))
        km = round(km, 1)
        self.km_real[(vid, comp)] = km
        rend = v["rend_base"] * float(np.clip(self.rng.normal(1, 0.03), 0.9, 1.1))
        if "deterioracao" in v["flags"] and comp >= "2026-01":
            rend *= v["fator_deterioracao"]
        dias = dias_do_mes(comp)
        # ---- abastecimentos (método tanque cheio: litros repõem o consumo desde o abastecimento anterior)
        restante = km
        eventos_comb = []
        while restante > 0.5:
            litros_alvo = c.tanque_l * self.u(c.fracao_abastecimento)
            dist = min(litros_alvo * rend, restante)
            sobra = restante - dist
            if 0 < sobra < 0.15 * litros_alvo * rend and (dist + sobra) / rend <= 0.95 * c.tanque_l:
                dist += sobra  # evita abastecimento residual minúsculo
            restante -= dist
            eventos_comb.append(dist)
        dias_ev = sorted(int(x) for x in self.rng.integers(1, dias + 1, size=len(eventos_comb)))
        ano, mes = int(comp[:4]), int(comp[5:])
        instantes = sorted(self.instante(date(ano, mes, dia)) for dia in dias_ev)  # mesma ordem do odômetro
        for dist, quando in zip(eventos_comb, instantes):
            rend_ev = rend * float(np.clip(self.rng.normal(1, 0.02), 0.94, 1.06))
            litros = round(dist / rend_ev, 2)
            self.odometro[vid] += int(round(dist))
            posto = self.escolher_posto(v)
            preco = round(PRECO_BASE[c.combustivel] * VARIACAO_MENSAL_PRECO[comp] * posto["fator"]
                          * float(np.exp(self.rng.normal(0, 0.004))), 3)
            valor = round(litros * preco, 2)
            d = quando.date()
            origem = self.origens_mensais[(emp, comp, "comb")]
            self.despesa(emp, frota, vid, origem, "COMBUSTIVEL", c.combustivel, d, valor,
                         f"{'DIESEL S10' if c.combustivel == 'diesel_s10' else 'GASOLINA C'} {posto['codigo']}",
                         posto["uf"], f"linha {len(self.t['abastecimentos']) + 2}",
                         sub=("abastecimentos", {
                             "data_hora": quando.isoformat(timespec="minutes"), "litros": litros,
                             "preco_litro": preco, "combustivel": c.combustivel,
                             "odometro_km": None if "sem_odometro" in v["flags"] else self.odometro[vid],
                             "posto_codigo": posto["codigo"], "posto_rede_negociada": posto["rede"],
                             "meio_pagamento": "cartao_frota"}))
        self.km_acum[vid] += km
        # ---- manutenção
        self.simular_manutencao(v, comp, km)
        # ---- pedágio
        if emp == "EMP-C":
            self.simular_viagens_pedagio_c(v, comp, km)
        else:
            self.simular_pedagio_passagens(v, comp, km)
        # ---- multas
        n_multas = int(self.rng.poisson(TAXA_MULTAS[emp]))
        for _ in range(n_multas):
            self.gerar_multa(v, comp)

    def escolher_posto(self, v):
        emp = v["empresa_id"]
        if "fora_rede" in v["flags"] and self.rng.random() < 0.45:
            return self.postos_fora_rede[int(self.rng.integers(0, len(self.postos_fora_rede)))]
        if self.rng.random() < 0.8:
            return self.postos[emp][int(self.rng.choice(v["postos_habituais"]))]
        return self.postos[emp][int(self.rng.integers(0, len(self.postos[emp])))]

    def simular_manutencao(self, v, comp, km):
        vid, emp = v["veiculo_id"], v["empresa_id"]
        c = CATEGORIAS[v["categoria_id"]]
        if v["propriedade"] == "locada":
            return  # manutenção inclusa na locação (cenário G30)
        eventos = []
        acum_ini = self.km_acum[vid] - km
        # preventiva por intervalo de km
        while self.prox_preventiva[vid] <= self.km_acum[vid]:
            self.n_preventivas[vid] += 1
            completa = self.n_preventivas[vid] % 4 == 0
            custo = self.u(c.preventiva_custo_brl) * (3.5 if completa else 1.0) * (1.1 if v["antigo"] else 1.0)
            frac = (self.prox_preventiva[vid] - acum_ini) / max(km, 1)
            eventos.append(("preventiva", "revisao_completa" if completa else "revisao_periodica", custo,
                            True, frac, "motor"))
            self.prox_preventiva[vid] += c.preventiva_intervalo_km
        while self.prox_pneus[vid] <= self.km_acum[vid]:
            frac = (self.prox_pneus[vid] - acum_ini) / max(km, 1)
            eventos.append(("pneus", "substituicao_pneus", self.u(c.pneus_custo_brl), True, frac, "pneus"))
            self.prox_pneus[vid] += c.pneus_intervalo_km
        mult_idade = 2.2 if v["antigo"] else 1.0
        n_corr = int(self.rng.poisson(c.corretiva_eventos_por_10mil_km * km / 10_000 * mult_idade))
        sistemas = ["freios", "suspensao", "eletrica", "motor", "transmissao", "arrefecimento"]
        for _ in range(n_corr):
            lo, hi = c.corretiva_custo_brl
            custo = float(np.clip(np.exp(self.rng.normal(np.log(np.sqrt(lo * hi)), 0.55)), lo, hi))
            eventos.append(("corretiva", "reparo", custo, False, self.u((0.0, 1.0)),
                            sistemas[int(self.rng.integers(0, len(sistemas)))]))
        if vid == "C-V20" and comp == "2025-11":  # cenário G25: sinistro (franquia)
            eventos.append(("funilaria_sinistro", "franquia_sinistro", 6_500.0, False, 0.5, "carroceria"))
        for tipo, sub, custo, programada, frac, sistema in eventos:
            frac = float(np.clip(frac, 0, 0.999))
            dia = 1 + int(frac * (dias_do_mes(comp) - 1))
            d = date(int(comp[:4]), int(comp[5:]), dia)
            odo = None if "sem_odometro" in v["flags"] else int(self.odometro[vid] - km * (1 - frac))
            if emp == "EMP-A":
                if comp not in ("2025-12", "2026-01", "2026-02"):
                    self.verdade_lacunas["G29"] += custo  # cenário G29: só há notas de 3 meses
                    self.verdade_lacunas["G29.manutencao"] += custo
                    continue
                conf = self.u((0.60, 0.98))
                origem = self.origem(emp, "imagem", f"foto_nota_oficina_{vid}_{d.isoformat()}.jpg",
                                     datetime(d.year, d.month, d.day, 18) + timedelta(days=2), "ocr", conf)
                ref = "imagem inteira"
            else:
                conf = None
                origem = self.origens_mensais[(emp, comp, "man")]
                ref = f"item {len(self.t['manutencoes']) + 1}"
            did = self.despesa(emp, v["frota_id"], vid, origem, "MANUTENCAO", sub, d, custo,
                               f"{sub.replace('_', ' ').upper()} {sistema.upper()}", "SP", ref, confianca=conf,
                               sub=("manutencoes", {"tipo": tipo, "programada": programada, "sistema": sistema,
                                                    "odometro_km": odo,
                                                    "oficina_codigo": f"OFIC-{emp[-1]}{int(self.rng.integers(1, 7)):02d}",
                                                    "dias_parado": int(self.rng.integers(0, 2 if tipo != 'corretiva' else 5))}))
            if vid == "B-V05" and sub == "revisao_completa":
                self.gab_g08 = did

    def simular_pedagio_passagens(self, v, comp, km):
        vid, emp = v["veiculo_id"], v["empresa_id"]
        c = CATEGORIAS[v["categoria_id"]]
        n = int(self.rng.poisson(km * DENSIDADE_PRACAS[self.cfg[emp]["modal"]] / 100))
        mult = 1 if c.classe_peso == "leve" else c.eixos
        origem = self.origens_mensais[(emp, comp, "ped")]
        usados: dict[str, list[datetime]] = defaultdict(list)
        for _ in range(n):
            if self.rng.random() < 0.85:
                praca = self.pracas[emp][int(self.rng.choice(v["rota_pracas"]))]
            else:
                praca = self.pracas[emp][int(self.rng.integers(0, len(self.pracas[emp])))]
            d = self.data_no_mes(comp)
            quando = self.instante(d, 5, 23)
            # o mesmo veículo não passa duas vezes pela mesma praça em menos de 90 minutos
            while any(abs((quando - t).total_seconds()) < 90 * 60 for t in usados[praca["codigo"]]):
                quando += timedelta(hours=2)
            usados[praca["codigo"]].append(quando)
            d = quando.date()
            valor = praca["tarifa"] * mult
            self.despesa(emp, v["frota_id"], vid, origem, "PEDAGIO", "passagem_tag", d, valor,
                         f"PEDAGIO {praca['codigo']}", "SP", f"linha {len(self.t['pedagios']) + 2}",
                         sub=("pedagios", {"data_hora": quando.isoformat(timespec="minutes"),
                                           "concessionaria_codigo": praca["concessionaria"],
                                           "praca_codigo": praca["codigo"], "qtd_passagens": 1,
                                           "eixos_cobrados": c.eixos if mult > 1 else 2,
                                           "meio_pagamento": "tag", "viagem_id": None}))

    def simular_viagens_pedagio_c(self, v, comp, km):
        vid, emp = v["veiculo_id"], v["empresa_id"]
        c = CATEGORIAS[v["categoria_id"]]
        restante = km
        p = pd.Period(comp, freq="M")
        distancias = []
        while restante > 50:
            dist = min(self.u((900, 1_900)), restante)
            restante -= dist
            distancias.append(dist)
        passo = p.days_in_month / max(len(distancias), 1)
        for k, dist in enumerate(distancias):
            dur = max(1, int(round(dist / 650)))
            inicio = date(p.year, p.month, min(p.days_in_month, 1 + int(k * passo)))
            fim = inicio + timedelta(days=dur)
            r = self.rng.random()
            tipo = "carregada_lotacao" if r < 0.55 else ("carregada_fracionada" if r < 0.75 else "retorno_vazio")
            vgm = self.proximo("VGM-C", 5)
            vp_recebido = None
            eixos_susp = 0
            if tipo == "carregada_lotacao":
                vp_recebido = bool(self.rng.random() >= 0.15)  # cenário G23
            if tipo == "retorno_vazio":
                eixos_susp = c.eixos_suspensiveis
            ufs = ["SP", "MG", "GO", "MT", "PR", "MS"]
            self.t["viagens"].append({
                "viagem_id": vgm, "veiculo_id": vid, "data_inicio": inicio.isoformat(), "data_fim": fim.isoformat(),
                "uf_origem": ufs[int(self.rng.integers(0, 6))], "uf_destino": ufs[int(self.rng.integers(0, 6))],
                "km_percorrido": round(dist, 1), "tipo_viagem": tipo, "vale_pedagio_recebido": vp_recebido,
                "eixos_suspensos_declarados": eixos_susp})
            n_pracas = int(self.rng.poisson(dist * DENSIDADE_PRACAS["rodoviario_longa_distancia"] / 100))
            if n_pracas == 0:
                continue
            tarifas = [self.pracas[emp][int(self.rng.integers(0, len(self.pracas[emp])))]["tarifa"]
                       for _ in range(n_pracas)]
            eixos_devidos = c.eixos - eixos_susp
            eixos_cobrados = eixos_devidos
            indevido = False
            if tipo == "retorno_vazio" and eixos_susp > 0 and self.rng.random() < 0.20:
                eixos_cobrados = c.eixos  # cenário G24: eixo suspenso cobrado
                indevido = True
            valor = sum(tarifas) * eixos_cobrados
            if tipo == "carregada_lotacao" and vp_recebido:
                meio, natureza = "vale_pedagio", "custeado_terceiro"
            elif "sem_tag" in v["flags"]:
                meio, natureza = "manual", "proprio"
            else:
                meio, natureza = "tag", "proprio"
            reg = {"tipo": tipo, "vgm": vgm, "valor": valor, "indevido": indevido,
                   "valor_devido": sum(tarifas) * eixos_devidos, "meio": meio, "natureza": natureza,
                   "n_pracas": n_pracas, "eixos_cobrados": eixos_cobrados, "inicio": inicio, "vid": vid,
                   "comp": comp, "vp": vp_recebido}
            self.registrar_pedagio_viagem_c(v, reg)

    def registrar_pedagio_viagem_c(self, v, r):
        emp, vid, comp = "EMP-C", v["veiculo_id"], r["comp"]
        d = r["inicio"]
        quando = self.instante(d)
        sub = {"data_hora": quando.isoformat(timespec="minutes"), "concessionaria_codigo": "VARIAS",
               "praca_codigo": "CONSOLIDADO_VIAGEM", "qtd_passagens": r["n_pracas"],
               "eixos_cobrados": r["eixos_cobrados"], "meio_pagamento": r["meio"], "viagem_id": r["vgm"]}
        if r["meio"] == "manual":
            # pedágio pago na cabine e reembolsado ao motorista; ~30% sem comprovante (cenário G22)
            u = self.rng.random()
            if u < 0.30:
                self.verdade_lacunas["G22"] += r["valor"]
                self.lacuna_g22.append(r["vgm"])
                return
            if u < 0.40:
                origem = self.origem(emp, "digitacao_manual", f"declaracao_motorista_{r['vgm']}", datetime(
                    d.year, d.month, d.day, 20) + timedelta(days=3), "manual")
                conf = None
            else:
                conf = self.u((0.65, 0.98))
                origem = self.origem(emp, "pdf_imagem", f"comprovantes_pedagio_{r['vgm']}.pdf", datetime(
                    d.year, d.month, d.day, 20) + timedelta(days=3), "ocr", conf)
            did = self.despesa(emp, v["frota_id"], vid, origem, "PEDAGIO", "pedagio_manual_reembolso", d, r["valor"],
                               f"REEMBOLSO PEDAGIO {r['vgm']}", "SP", "documento inteiro", confianca=conf,
                               sub=("pedagios", sub))
        else:
            if comp == "2026-02" and r["meio"] == "tag":
                self.verdade_lacunas["G21"] += r["valor"]  # extrato de fevereiro ausente
                return
            origem = self.origens_mensais.get((emp, comp, "ped")) if r["meio"] == "tag" else \
                self.origens_mensais[(emp, comp, "tms")]
            if origem is None:
                return
            sub_cat = "viagem_tag" if r["meio"] == "tag" else "viagem_vale_pedagio"
            did = self.despesa(emp, v["frota_id"], vid, origem, "PEDAGIO", sub_cat, d, r["valor"],
                               f"PEDAGIO VIAGEM {r['vgm']}", "SP", f"linha {len(self.t['pedagios']) + 2}",
                               natureza=r["natureza"], sub=("pedagios", sub))
        if r["indevido"]:
            self.g24.append((did, r["valor"] - r["valor_devido"]))
        if r["tipo"] == "carregada_lotacao" and r["vp"] is False:
            self.g23.append((did, r["valor"]))

    def gerar_multa(self, v, comp):
        vid, emp = v["veiculo_id"], v["empresa_id"]
        grav = str(self.rng.choice(list(DIST_GRAVIDADE), p=list(DIST_GRAVIDADE.values())))
        valor_orig = MULTA_VALOR[grav]
        d_inf = self.data_no_mes(comp)
        d_not = d_inf + timedelta(days=int(self.rng.integers(10, 30)))
        prazo = d_not + timedelta(days=PRAZO_INDICACAO)
        venc = d_not + timedelta(days=int(self.rng.integers(30, 46)))
        r = self.rng.random()
        p_prazo, p_sne = (0.70, 0.10) if emp == "EMP-B" else (0.80, 0.12)
        if r < p_sne:
            desc, pago = 0.40, venc - timedelta(days=int(self.rng.integers(1, 10)))
        elif r < p_sne + p_prazo:
            desc, pago = 0.20, venc - timedelta(days=int(self.rng.integers(0, 10)))
        else:
            desc, pago = 0.0, venc + timedelta(days=int(self.rng.integers(5, 40)))
        valor_pago = round(valor_orig * (1 - desc), 2)
        if emp == "EMP-A":
            self.verdade_lacunas["G29"] += valor_pago  # multas existem, mas não foram enviadas
            self.verdade_lacunas["G29.multas"] += valor_pago
            return
        origem = self.origem_multas_b if emp == "EMP-B" else self.origem_multas_c
        auto = token(f"AIT|{vid}|{d_inf}|{self.rng.random()}", "AIT")
        identificado = True
        condutor = str(self.rng.choice(v["motoristas"]))
        did = self.despesa(emp, v["frota_id"], vid, origem, "MULTA", "infracao_transito", d_inf, valor_pago,
                           f"MULTA {grav.upper()} {auto}", "SP", f"linha {len(self.t['multas']) + 2}",
                           sub=("multas", {"auto_infracao_token": auto, "tipo_multa": "original",
                                           "multa_origem_despesa_id": None, "gravidade": grav,
                                           "valor_original": valor_orig, "data_notificacao": d_not.isoformat(),
                                           "prazo_indicacao_condutor": prazo.isoformat(),
                                           "condutor_identificado": identificado,
                                           "condutor_token": condutor,
                                           "data_vencimento": venc.isoformat(), "data_pagamento": pago.isoformat(),
                                           "valor_pago": valor_pago, "desconto_aplicado": desc,
                                           "situacao": "paga"}))
        if desc == 0.0:
            self.multas_sem_desconto.append(did)

    def gerar_nics(self):
        """Converte multas sorteadas em casos sem indicação do condutor e lança a multa NIC.

        CTB, art. 257, § 8º (Lei nº 14.229/2021): nova multa de 2 vezes a originária para pessoa
        jurídica que não indica o condutor no prazo do § 7º (30 dias da notificação)."""
        idx = {d["despesa_id"]: d for d in self.t["despesas"]}
        for emp, qtd, limite in (("EMP-B", 6, "2026-01"), ("EMP-C", 2, "2026-01")):
            elegiveis = [m for m in self.t["multas"] if m["despesa_id"].startswith(f"DSP-{emp[-1]}")
                         and m["tipo_multa"] == "original" and idx[m["despesa_id"]]["data_evento"][:7] <= limite]
            for pos in sorted(self.rng.choice(len(elegiveis), size=qtd, replace=False)):
                m = elegiveis[int(pos)]
                orig = idx[m["despesa_id"]]
                m["condutor_identificado"] = False
                m["condutor_token"] = None
                prazo = date.fromisoformat(m["prazo_indicacao_condutor"])
                d_nic = prazo + timedelta(days=int(self.rng.integers(20, 45)))
                venc_nic = d_nic + timedelta(days=35)
                valor_nic_orig = round(2 * m["valor_original"], 2)
                valor_nic = round(valor_nic_orig * 0.8, 2)
                nic = self.despesa(emp, orig["frota_id"], orig["veiculo_id"], orig["origem_id"], "MULTA",
                                   "multa_nic", d_nic, valor_nic, f"MULTA NIC REF {m['auto_infracao_token']}", "SP",
                                   f"linha {len(self.t['multas']) + 2}",
                                   sub=("multas", {"auto_infracao_token": token(f"NIC|{m['auto_infracao_token']}", "AIT"),
                                                   "tipo_multa": "nic", "multa_origem_despesa_id": m["despesa_id"],
                                                   "gravidade": m["gravidade"], "valor_original": valor_nic_orig,
                                                   "data_notificacao": d_nic.isoformat(),
                                                   "prazo_indicacao_condutor": None, "condutor_identificado": None,
                                                   "condutor_token": None, "data_vencimento": venc_nic.isoformat(),
                                                   "data_pagamento": (venc_nic - timedelta(days=3)).isoformat(),
                                                   "valor_pago": valor_nic, "desconto_aplicado": 0.20,
                                                   "situacao": "paga"}))
                self.nics.append(nic)

    def simular_tributos_seguros_outros(self):
        # IPVA e licenciamento (EMP-B e EMP-C; EMP-A não enviou: cenário G29)
        meses_a = len(self.cfg["EMP-A"]["comps"])
        for vid, v in self.veiculos.items():
            emp = v["empresa_id"]
            if emp == "EMP-A" and v["propriedade"] == "propria":
                c = CATEGORIAS[v["categoria_id"]]
                tributos = v["valor_referencia_brl"] * (1 + DEPRECIACAO_ANUAL / 2) * c.aliquota_ipva + LICENCIAMENTO
                seguro = v["valor_referencia_brl"] * self.u(c.taxa_seguro_anual)
                self.verdade_lacunas["G29"] += (tributos + seguro) * meses_a / 12  # por competência
                self.verdade_lacunas["G29.tributos"] += tributos * meses_a / 12
                self.verdade_lacunas["G29.seguro"] += seguro * meses_a / 12
                continue
            if emp == "EMP-A" or v["propriedade"] != "propria":
                continue
            c = CATEGORIAS[v["categoria_id"]]
            for exercicio in (2025, 2026):
                base = v["valor_referencia_brl"] * ((1 + DEPRECIACAO_ANUAL) if exercicio == 2025 else 1.0)
                ipva = base * c.aliquota_ipva
                orig = self.origem(emp, "pdf_texto", f"comprovantes_ipva_licenciamento_{exercicio}_{vid}.pdf",
                                   datetime(exercicio, 4, 28, 15), "leitura_estruturada", 0.99)
                for parcela in (1, 2, 3):
                    d = date(exercicio, parcela, 15)
                    self.despesa(emp, v["frota_id"], vid, orig, "TRIBUTO", "ipva", d, ipva / 3,
                                 f"IPVA {exercicio} PARCELA {parcela}/3", "SP", f"página {parcela}",
                                 comp_ini=f"{exercicio}-01", comp_fim=f"{exercicio}-12",
                                 sub=("tributos", {"tipo": "ipva", "exercicio": exercicio, "parcela": parcela,
                                                   "total_parcelas": 3, "base_calculo_brl": round(base, 2),
                                                   "aliquota_hipotese": c.aliquota_ipva}))
                d = date(exercicio, 4, 20)
                self.despesa(emp, v["frota_id"], vid, orig, "TRIBUTO", "licenciamento", d, LICENCIAMENTO,
                             f"LICENCIAMENTO {exercicio}", "SP", "página 4", comp_ini=f"{exercicio}-01",
                             comp_fim=f"{exercicio}-12",
                             sub=("tributos", {"tipo": "licenciamento", "exercicio": exercicio, "parcela": 1,
                                               "total_parcelas": 1, "base_calculo_brl": None,
                                               "aliquota_hipotese": None}))
        # Seguro EMP-B: apólice anual paga à vista (cenário G07)
        veics_b = [v for v in self.veiculos.values() if v["empresa_id"] == "EMP-B"]
        premio = sum(v["valor_referencia_brl"] * self.u(CATEGORIAS[v["categoria_id"]].taxa_seguro_anual)
                     for v in veics_b)
        for ini, fator in (("2025-04", 1.0), ("2026-04", 1.06)):
            p = pd.Period(ini, freq="M")
            fim = str(p + 11)
            orig = self.origem("EMP-B", "pdf_texto", f"apolice_frota_{ini}.pdf", datetime(p.year, p.month, 8, 11),
                               "leitura_estruturada", 0.98)
            did = self.despesa("EMP-B", "FRO-B1", None, orig, "SEGURO", "apolice_frota", date(p.year, p.month, 5),
                               premio * fator, f"PREMIO SEGURO FROTA VIGENCIA {ini} A {fim}", "SP", "página 1",
                               comp_ini=ini, comp_fim=fim,
                               sub=("seguros", {"apolice_token": token(f"apolice|B|{ini}", "APL"),
                                                "tipo_cobertura": "frota_coletiva",
                                                "vigencia_inicio": f"{ini}-01",
                                                "vigencia_fim": str(pd.Period(fim, freq='M').end_time.date()),
                                                "premio_total_brl": round(premio * fator, 2), "parcela": 1,
                                                "total_parcelas": 1, "veiculos_cobertos": len(veics_b)}))
            if ini == "2026-04":
                self.g07 = did
        # Seguro EMP-C: parcelas mensais
        veics_c = [v for v in self.veiculos.values() if v["empresa_id"] == "EMP-C"]
        premio_c = sum(v["valor_referencia_brl"] * self.u(CATEGORIAS[v["categoria_id"]].taxa_seguro_anual)
                       for v in veics_c)
        for comp in self.cfg["EMP-C"]["comps"]:
            fator = 1.05 if comp >= "2026-03" else 1.0
            ini_vig = "2025-03" if comp < "2026-03" else "2026-03"
            d = date(int(comp[:4]), int(comp[5:]), 10)
            self.despesa("EMP-C", "FRO-C1", None, self.origens_mensais[("EMP-C", comp, "seg")], "SEGURO",
                         "parcela_apolice_frota", d, premio_c * fator / 12, f"SEGURO FROTA PARCELA {comp}", "SP",
                         "página 1", sub=("seguros", {"apolice_token": token(f"apolice|C|{ini_vig}", "APL"),
                                                       "tipo_cobertura": "frota_coletiva",
                                                       "vigencia_inicio": f"{ini_vig}-01",
                                                       "vigencia_fim": str((pd.Period(ini_vig, freq='M') + 11).end_time.date()),
                                                       "premio_total_brl": round(premio_c * fator, 2),
                                                       "parcela": int((pd.Period(comp, freq='M') - pd.Period(ini_vig, freq='M')).n) + 1,
                                                       "total_parcelas": 12, "veiculos_cobertos": len(veics_c)}))
        # Outros custos
        for comp in self.cfg["EMP-A"]["comps"]:
            for vid in ["A-V07", "A-V08"]:
                d = date(int(comp[:4]), int(comp[5:]), 5)
                self.despesa("EMP-A", "FRO-A1", vid, self.origens_mensais[("EMP-A", comp, "loc")], "OUTROS",
                             "locacao_veiculo", d, LOCACAO_MENSAL, f"LOCACAO {vid} {comp}", "SP",
                             "página 1")
            for _ in range(int(self.rng.integers(2, 6))):
                vid = f"A-V{int(self.rng.integers(1, 9)):02d}"
                d = self.data_no_mes(comp)
                self.despesa("EMP-A", "FRO-A1", vid, self.origens_mensais[("EMP-A", comp, "txt")], "OUTROS",
                             "estacionamento", d, round(self.u((20, 60)), 2), f"estacionamento cliente {vid}",
                             "SP", "mensagem", confianca=self.u((0.85, 0.99)))
        for comp in self.cfg["EMP-B"]["comps"]:
            for v in veics_b:
                if self.rng.random() < 0.65:
                    d = self.data_no_mes(comp)
                    self.despesa("EMP-B", "FRO-B1", v["veiculo_id"], self.origens_mensais[("EMP-B", comp, "txt")],
                                 "OUTROS", "lavagem", d, round(self.u((70, 140)), 2),
                                 f"lavagem {v['veiculo_id']} ok", "SP", "mensagem",
                                 confianca=self.u((0.82, 0.99)))
        for comp in self.cfg["EMP-C"]["comps"]:
            d = date(int(comp[:4]), int(comp[5:]), 8)
            self.despesa("EMP-C", "FRO-C1", None, self.origens_mensais[("EMP-C", comp, "tel")], "OUTROS",
                         "telemetria", d, TELEMETRIA * len(veics_c), f"TELEMETRIA {len(veics_c)} VEICULOS {comp}",
                         "SP", "página 1")

    # ---------------- uso mensal ----------------
    def registrar_uso(self):
        faltantes = {("B-V08", "2025-12"), ("B-V08", "2026-01"), ("B-V19", "2026-05")}  # cenário G09
        for (vid, comp), km in sorted(self.km_real.items()):
            v = self.veiculos[vid]
            emp = v["empresa_id"]
            fonte = "telemetria" if emp == "EMP-C" else "odometro_abastecimento"
            disponivel = "sem_odometro" not in v["flags"] and (vid, comp) not in faltantes
            self.t["uso_veiculo_mensal"].append({
                "uso_id": self.proximo(f"USO-{emp[-1]}", 5), "veiculo_id": vid, "competencia": comp,
                "km_rodados": km if disponivel else None, "fonte_km": fonte if disponivel else None,
                "status_valor": "OBSERVADO" if disponivel else "NAO_DISPONIVEL",
                "dias_em_operacao": int(self.rng.integers(18, 23)) if emp == "EMP-A" else int(self.rng.integers(20, 27))})
        # nos meses sem km da EMP-B, o odômetro também não foi informado nos abastecimentos
        idx = {d["despesa_id"]: d for d in self.t["despesas"]}
        for ab in self.t["abastecimentos"]:
            dsp = idx[ab["despesa_id"]]
            if (dsp["veiculo_id"], dsp["data_evento"][:7]) in faltantes:
                ab["odometro_km"] = None

    # ---------------- injeção de problemas ----------------
    def injetar(self):
        rng = self.rng
        desp = self.t["despesas"]
        idx = {d["despesa_id"]: d for d in desp}
        abast = {a["despesa_id"]: a for a in self.t["abastecimentos"]}

        # G01 - arquivo de março (EMP-B) enviado duas vezes
        orig_mar = self.origens_mensais[("EMP-B", "2026-03", "comb")]
        o = next(x for x in self.t["origens_dados"] if x["origem_id"] == orig_mar)
        orig_dup = self.origem("EMP-B", "xlsx", o["descricao"], datetime(2026, 4, 9, 16), "leitura_estruturada",
                               hash_de=f"EMP-B|{o['descricao']}")
        novos = []
        for d in [d for d in desp if d["origem_id"] == orig_mar]:
            nd = dict(d)
            nd["despesa_id"] = self.proximo("DSP-B", 6)
            nd["origem_id"] = orig_dup
            desp.append(nd)
            self.t["abastecimentos"].append({**abast[d["despesa_id"]], "despesa_id": nd["despesa_id"]})
            novos.append(nd["despesa_id"])
        self.cenario("G01", "EMP-B", "problema_dado", "erro_de_dado",
                     "Planilha de abastecimentos de mar/2026 enviada duas vezes (mesmo hash); registros duplicados.",
                     "R-DUP-ARQ", novos, valor_real=self.soma(novos))

        # G02 - cobrança duplicada de passagem (EMP-B)
        ped_b = [p for p in self.t["pedagios"] if p["despesa_id"].startswith("DSP-B")]
        escolhidos = rng.choice(len(ped_b), size=15, replace=False)
        dups, valor = [], 0.0
        for i in escolhidos:
            p = ped_b[int(i)]
            d = idx[p["despesa_id"]]
            nd = dict(d)
            nd["despesa_id"] = self.proximo("DSP-B", 6)
            quando = datetime.fromisoformat(p["data_hora"]) + timedelta(minutes=int(rng.integers(0, 3)))
            desp.append(nd)
            self.t["pedagios"].append({**p, "despesa_id": nd["despesa_id"],
                                       "data_hora": quando.isoformat(timespec="minutes")})
            dups.append(nd["despesa_id"])
            valor += d["valor_brl"]
        self.cenario("G02", "EMP-B", "problema_dado", "oportunidade_validavel",
                     "Passagens cobradas duas vezes na mesma praça em até 3 minutos (contestação junto ao emissor).",
                     "R-PED-DUP", dups, valor_real=valor)

        # G03 - multas NIC e G04 - multas pagas sem desconto
        self.cenario("G03", "EMP-B", "achado_negocio", "oportunidade_validavel",
                     "Multas NIC (CTB art. 257, § 8º) por não indicação do condutor no prazo: custo evitável por processo.",
                     "Regra de negócio REC-01", [n for n in self.nics if n.startswith("DSP-B")],
                     valor_real=sum(idx[n]["valor_brl"] for n in self.nics if n.startswith("DSP-B")))
        sem_desc_b = [m for m in self.multas_sem_desconto if m.startswith("DSP-B")]
        self.cenario("G04", "EMP-B", "achado_negocio", "oportunidade_validavel",
                     "Multas pagas após o vencimento, sem o desconto de 20% (CTB art. 284).",
                     "Regra de negócio REC-02", sem_desc_b,
                     valor_real=sum(idx[m]["valor_brl"] * 0.20 for m in sem_desc_b))

        # G05 a G09, G25, G26, G30 - situações operacionais (sem alteração de registros)
        self.cenario("G05", "EMP-B", "achado_negocio", "candidato_investigacao",
                     "Três utilitários com quilometragem muito baixa (B-V28 a B-V30): hipótese de subutilização.",
                     "Indicador IND-11 (utilização) e regra REC-11", ["B-V28", "B-V29", "B-V30"], tabela="veiculos")
        self.cenario("G06", "EMP-B", "achado_negocio", "candidato_investigacao",
                     "Caminhões toco de 2012-2013 (B-V11 a B-V14) com taxa de manutenção corretiva elevada.",
                     "Indicador IND-06 e regra REC-10", ["B-V11", "B-V12", "B-V13", "B-V14"], tabela="veiculos")
        self.cenario("G07", "EMP-B", "justificavel", "custo_justificavel",
                     "Renovação anual do seguro paga à vista em abr/2026: pico de caixa, não de custo por competência.",
                     "Rateio por competência (competencia_inicio/fim)", [self.g07])
        self.cenario("G08", "EMP-B", "justificavel", "custo_justificavel",
                     "Revisão completa programada de B-V05: custo alto no mês, coerente com o plano preventivo.",
                     "Classificação por tipo/programada antes do teste de anomalia", [self.gab_g08])
        self.cenario("G09", "EMP-B", "lacuna", "lacuna_de_dados",
                     "Quilometragem ausente de B-V08 (dez/2025 e jan/2026) e B-V19 (mai/2026).",
                     "Completude de contexto (dimensão X)", ["B-V08|2025-12", "B-V08|2026-01", "B-V19|2026-05"],
                     tabela="uso_veiculo_mensal")

        # G10 - litros ausentes, preço presente (EMP-B)
        origem_de = {d["despesa_id"]: d["origem_id"] for d in desp}
        cand = [a for a in self.t["abastecimentos"] if a["despesa_id"].startswith("DSP-B")
                and origem_de[a["despesa_id"]] not in (orig_mar, orig_dup)]
        escolhidos = rng.choice(len(cand), size=20, replace=False)
        g10 = []
        for i in escolhidos:
            cand[int(i)]["litros"] = None
            g10.append(cand[int(i)]["despesa_id"])
        self.cenario("G10", "EMP-B", "problema_dado", "lacuna_de_dados",
                     "Abastecimentos sem litros, com preço e valor presentes: litros derivável por regra (imputação "
                     "determinística identificada).", "R-CAMPO-AUSENTE + imputação IMP-01", g10)

        # EMP-C
        ab_c = [a for a in self.t["abastecimentos"] if a["despesa_id"].startswith("DSP-C")]
        usados: set[str] = set()

        def sortear(n):
            livres = [a for a in ab_c if a["despesa_id"] not in usados and idx[a["despesa_id"]]["valor_brl"] > 0]
            pos = rng.choice(len(livres), size=n, replace=False)
            sel = [livres[int(p)] for p in pos]
            usados.update(a["despesa_id"] for a in sel)
            return sel

        # G11 - duplicidade entre fontes (extrato do cartão e NF-e em PDF)
        g11 = []
        for a in sortear(40):
            d = idx[a["despesa_id"]]
            nf = self.origem("EMP-C", "pdf_texto", f"nfe_{d['despesa_id']}.pdf",
                             datetime.fromisoformat(a["data_hora"]) + timedelta(days=6), "leitura_estruturada", 0.97)
            nd = dict(d)
            nd["despesa_id"] = self.proximo("DSP-C", 6)
            nd["origem_id"] = nf
            nd["referencia_na_origem"] = "página 1"
            nd["descricao_original"] = f"NF-E {token(d['despesa_id'], 'NF', 6)} OLEO DIESEL B S10"
            desp.append(nd)
            quando = datetime.fromisoformat(a["data_hora"]) + timedelta(minutes=int(rng.integers(2, 9)))
            self.t["abastecimentos"].append({**a, "despesa_id": nd["despesa_id"],
                                             "data_hora": quando.isoformat(timespec="minutes")})
            g11.append(nd["despesa_id"])
        self.cenario("G11", "EMP-C", "problema_dado", "erro_de_dado",
                     "Mesma transação presente no extrato do cartão e na NF-e (PDF): conciliar, não somar.",
                     "R-DUP-REG", g11, valor_real=self.soma(g11))

        # G14 - litros multiplicados por 10 (erro de separador decimal)
        g14 = []
        for a in sortear(5):
            a["litros"] = round(a["litros"] * 10, 2)
            g14.append(a["despesa_id"])
        self.cenario("G14", "EMP-C", "problema_dado", "erro_de_dado",
                     "Litros multiplicados por 10 (separador decimal): volume acima da capacidade do tanque.",
                     "R-ABS-TANQUE e R-CONC-VALOR", g14)
        # G15 - odômetro regressivo (dígitos trocados)
        g15 = []
        for a in sortear(6):
            a["odometro_km"] = a["odometro_km"] - 30_000  # dígito digitado errado
            g15.append(a["despesa_id"])
        self.cenario("G15", "EMP-C", "problema_dado", "erro_de_dado",
                     "Odômetro menor que o do abastecimento anterior (digitação).", "R-ODO-REG", g15)
        # G16 - data no futuro
        g16 = []
        for a in sortear(2):
            d = idx[a["despesa_id"]]
            d["data_evento"] = "2027" + d["data_evento"][4:]
            d["competencia_inicio"] = d["competencia_fim"] = d["data_evento"][:7]
            a["data_hora"] = "2027" + a["data_hora"][4:]
            g16.append(a["despesa_id"])
        self.cenario("G16", "EMP-C", "problema_dado", "erro_de_dado",
                     "Ano digitado como 2027: data posterior ao recebimento do arquivo.", "R-DATA-FUT", g16)
        # G17 - preço por litro com vírgula deslocada (valor total correto)
        g17 = []
        for a in sortear(3):
            a["preco_litro"] = round(a["preco_litro"] * 10, 3)
            g17.append(a["despesa_id"])
        self.cenario("G17", "EMP-C", "problema_dado", "erro_de_dado",
                     "Preço por litro com casa decimal deslocada; valor total permanece correto.",
                     "R-PRECO-FAIXA e R-CONC-VALOR", g17)
        # G18 - veículo fora do cadastro
        g18 = []
        for a in sortear(4):
            idx[a["despesa_id"]]["veiculo_id"] = "C-V99"
            a["odometro_km"] = None
            g18.append(a["despesa_id"])
        self.cenario("G18", "EMP-C", "problema_dado", "erro_de_dado",
                     "Abastecimentos de veículo inexistente no cadastro (possível agregado ou cartão emprestado).",
                     "R-VEIC-DESC", g18)
        # G19 - combustível incompatível
        g19 = []
        for a in sortear(2):
            a["combustivel"] = "gasolina"
            a["preco_litro"] = round(PRECO_BASE["gasolina"] * 1.01, 3)
            a["litros"] = round(self.u((35, 55)), 2)
            d = idx[a["despesa_id"]]
            d["valor_brl"] = round(a["litros"] * a["preco_litro"], 2)
            d["subcategoria"] = "gasolina"
            d["descricao_original"] = "GASOLINA C " + d["descricao_original"].split()[-1]
            a["odometro_km"] = None
            g19.append(a["despesa_id"])
        self.cenario("G19", "EMP-C", "problema_dado", "candidato_investigacao",
                     "Gasolina lançada em cartão de caminhão a diesel: erro de cadastro ou uso indevido do cartão.",
                     "R-COMB-INCOMP", g19)
        # G20 - valores negativos (2 estornos legítimos, 1 sinal invertido)
        g20, g33 = [], []
        alvo = sortear(3)
        for k, a in enumerate(alvo):
            d = idx[a["despesa_id"]]
            if k < 2:
                # crédito de ajuste de preço negociado: estorno legítimo, sem litros associados
                nd = dict(d)
                nd["despesa_id"] = self.proximo("DSP-C", 6)
                nd["valor_brl"] = -round(d["valor_brl"] * 0.03, 2)
                nd["subcategoria"] = "estorno_ajuste_preco"
                nd["descricao_original"] = "ESTORNO AJUSTE PRECO REF " + d["despesa_id"]
                nd["data_evento"] = (date.fromisoformat(d["data_evento"]) + timedelta(days=12)).isoformat()
                nd["competencia_inicio"] = nd["competencia_fim"] = d["competencia_inicio"]
                desp.append(nd)
                g33.append(nd["despesa_id"])
            else:
                d["valor_brl"] = -d["valor_brl"]  # sinal invertido na extração
                g20.append(d["despesa_id"])
        self.cenario("G20", "EMP-C", "problema_dado", "erro_de_dado",
                     "Valor de abastecimento com sinal invertido na extração.", "R-VALOR-NEG", g20)
        self.cenario("G33", "EMP-C", "controle_negativo", "custo_justificavel",
                     "Dois créditos de ajuste de preço (estornos legítimos, identificados na descrição).",
                     "Nenhuma regra deve marcar (controle negativo de R-VALOR-NEG)", g33)

        # G12, G13 - consumo e preço
        self.cenario("G12", "EMP-C", "achado_negocio", "candidato_investigacao",
                     "C-V07, C-V15 e C-V22: rendimento (km/L) cai 12% a 17% a partir de jan/2026.",
                     "IND-07 + mudança persistente (CUSUM) + decomposição LMDI", ["C-V07", "C-V15", "C-V22"],
                     tabela="veiculos")
        self.cenario("G13", "EMP-C", "achado_negocio", "oportunidade_validavel",
                     "Cinco cavalos abastecem com frequência em postos fora da rede, 7% a 10% mais caros.",
                     "Efeito preço (LMDI) e comparação com a mediana de preço da própria frota",
                     ["C-V03", "C-V09", "C-V18", "C-V24", "C-V27"], tabela="veiculos")
        self.cenario("G21", "EMP-C", "lacuna", "lacuna_de_dados",
                     "Extrato de pedágio por tag de fev/2026 não enviado.", "Completude por categoria x mês",
                     ["EMP-C|PEDAGIO|2026-02"], tabela="lacunas", valor_real=self.verdade_lacunas["G21"])
        self.cenario("G22", "EMP-C", "lacuna", "lacuna_de_dados",
                     "Pedágios pagos em cabine sem comprovante (veículos sem tag).", "Completude + rastreabilidade",
                     self.lacuna_g22, tabela="viagens", valor_real=self.verdade_lacunas["G22"])
        baixa_c = [d["despesa_id"] for d in desp if d["empresa_id"] == "EMP-C" and d["requer_revisao"]]
        self.cenario("G32", "EMP-C", "problema_dado", "erro_de_dado",
                     "Comprovantes de pedágio pago em cabine lidos por OCR com confiança abaixo de 0,80.",
                     "R-CONF-EXTRACAO", baixa_c)
        self.cenario("G23", "EMP-C", "achado_negocio", "candidato_investigacao",
                     "Viagens carregadas por contratação de lotação sem registro de Vale-Pedágio, com pedágio pago "
                     "pela própria transportadora.", "Regra REC-09 (requer validação contratual e jurídica)",
                     [d for d, _ in self.g23], valor_real=sum(v for _, v in self.g23))
        self.cenario("G24", "EMP-C", "achado_negocio", "oportunidade_validavel",
                     "Retornos vazios com eixos suspensos declarados, mas cobrança de todos os eixos.",
                     "Regra REC-08 (Lei 13.103/2015, art. 17)", [d for d, _ in self.g24],
                     valor_real=sum(v for _, v in self.g24))
        self.cenario("G25", "EMP-C", "justificavel", "custo_justificavel",
                     "Franquia de sinistro de C-V20 em nov/2025: despesa extraordinária, excluída da linha de base.",
                     "Marcação de evento extraordinário",
                     [d["despesa_id"] for d in desp if d["veiculo_id"] == "C-V20" and d["subcategoria"] == "franquia_sinistro"])
        self.cenario("G26", "EMP-C", "justificavel", "custo_justificavel",
                     "C-V01 e C-V02 rodam ~25% acima dos pares: custo total alto por volume, custo/km normal.",
                     "Normalização por km e efeito atividade (LMDI)", ["C-V01", "C-V02"], tabela="veiculos")
        # EMP-A
        self.cenario("G27", "EMP-A", "lacuna", "lacuna_de_dados",
                     "Três utilitários sem odômetro: custo por km indisponível para eles.",
                     "Completude de contexto (dimensão X)", ["A-V02", "A-V03", "A-V04"], tabela="veiculos")
        # notas de oficina fotografadas (OCR): duas com baixa confiança aguardando revisão humana (G28)
        # e duas já revisadas e corrigidas por pessoa, com o valor extraído preservado (G34)
        ocr_a = sorted(d["despesa_id"] for d in desp if d["empresa_id"] == "EMP-A"
                       and d["categoria_custo"] == "MANUTENCAO")
        for did in ocr_a:
            idx[did]["requer_revisao"] = False
            idx[did]["confianca_extracao"] = max(idx[did]["confianca_extracao"], 0.81)
        pendentes, corrigidos = ocr_a[:2], ocr_a[2:4]
        for did, conf in zip(pendentes, (0.62, 0.71)):
            idx[did]["confianca_extracao"] = conf
            idx[did]["requer_revisao"] = True
        for did in corrigidos:
            d = idx[did]
            d["valor_extraido_original"] = round(d["valor_brl"] * 10, 2)  # vírgula lida como milhar
            d["status_valor"] = "CORRIGIDO"
            d["confianca_extracao"] = 0.66
        self.cenario("G28", "EMP-A", "problema_dado", "erro_de_dado",
                     "Notas de oficina fotografadas com confiança de extração abaixo de 0,80: fila de revisão humana.",
                     "R-CONF-EXTRACAO", pendentes)
        self.cenario("G34", "EMP-A", "controle_negativo", "custo_justificavel",
                     "Notas já corrigidas por pessoa: valor extraído original preservado, status CORRIGIDO.",
                     "Nenhuma regra deve marcar (correção humana rastreável)", corrigidos)
        self.cenario("G29", "EMP-A", "lacuna", "lacuna_de_dados",
                     "Sem dados de seguro, IPVA/licenciamento e multas; manutenção só de dez/2025 a fev/2026.",
                     "Estimativa progressiva (faixa) + perguntas guiadas", ["EMP-A"], tabela="empresas",
                     valor_real=self.verdade_lacunas["G29"],
                     observacao="valor_real = custo por competência não enviado (manutenção fora dos 3 meses, "
                                "multas, IPVA, licenciamento e seguro dos veículos próprios)")
        self.cenario("G30", "EMP-A", "justificavel", "custo_justificavel",
                     "Automóveis locados (A-V07, A-V08): manutenção e seguro inclusos na locação; não comparar "
                     "manutenção com veículos próprios.", "Regra de comparabilidade BEN-03", ["A-V07", "A-V08"],
                     tabela="veiculos")
        self.cenario("G31", "EMP-A", "lacuna", "lacuna_de_dados",
                     "Últimos dados de mar/2026 para análise em jul/2026: atualidade baixa.",
                     "Dimensão A (atualidade)", ["EMP-A"], tabela="empresas")

    # ---------------- saída ----------------
    def contar_registros_por_origem(self):
        cont = Counter(d["origem_id"] for d in self.t["despesas"])
        for o in self.t["origens_dados"]:
            o["registros_extraidos"] = cont.get(o["origem_id"], 0)

    def gravar(self, saida: Path):
        saida.mkdir(parents=True, exist_ok=True)
        ordem = ["empresas", "frotas", "categorias_veiculo", "veiculos", "uso_veiculo_mensal", "origens_dados",
                 "despesas", "abastecimentos", "manutencoes", "pedagios", "multas", "tributos", "seguros",
                 "viagens"]
        resumo = {}
        for nome in ordem:
            df = pd.DataFrame(self.t[nome])
            df.to_csv(saida / f"{nome}.csv", index=False, encoding="utf-8")
            resumo[nome] = int(len(df))
        pd.DataFrame(self.gab_cenarios).to_csv(saida / "gabarito_cenarios.csv", index=False, encoding="utf-8")
        pd.DataFrame(self.gab_registros).to_csv(saida / "gabarito_registros.csv", index=False, encoding="utf-8")
        pd.DataFrame(PARAMETROS).to_csv(saida.parent / "parametros-simulacao.csv", index=False, encoding="utf-8")
        (saida / "gabarito_lacunas.json").write_text(json.dumps(
            {k: round(v, 2) for k, v in sorted(self.verdade_lacunas.items())}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        meta = {
            "descricao": "Massa de dados sintéticos do Frota Pulse (Sprint 1). Dados fictícios.",
            "semente": SEMENTE, "data_referencia_analise": DATA_REFERENCIA_ANALISE,
            "periodos": {e: [c["comps"][0], c["comps"][-1]] for e, c in self.cfg.items()},
            "linhas_por_tabela": resumo, "cenarios_injetados": len(self.gab_cenarios),
            "formato": "CSV UTF-8, separador vírgula, decimal ponto, datas ISO 8601",
            "gerador": "src/gerar_dados_sinteticos.py"}
        (saida / "metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")
        return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=RAIZ / "data" / "sintetico")
    args = ap.parse_args()
    g = Gerador()
    g.nics, g.multas_sem_desconto, g.g23, g.g24, g.lacuna_g22 = [], [], [], [], []
    g.cadastrar()
    g.simular()
    g.gerar_nics()
    g.registrar_uso()
    g.injetar()
    g.contar_registros_por_origem()
    meta = g.gravar(args.saida)
    print(json.dumps(meta["linhas_por_tabela"], ensure_ascii=False))
    print(f"cenários: {meta['cenarios_injetados']}")


if __name__ == "__main__":
    main()

"""Implementação de referência dos métodos descritos na documentação do Frota Pulse.

Não é a aplicação. Serve para calcular, de forma reproduzível, os exemplos numéricos da
documentação a partir da massa sintética. Os identificadores (R-*, IMP-*, IND-*, REC-*)
são os mesmos usados em docs/.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

TABELAS = ["empresas", "frotas", "categorias_veiculo", "veiculos", "uso_veiculo_mensal", "origens_dados",
           "despesas", "abastecimentos", "manutencoes", "pedagios", "multas", "tributos", "seguros", "viagens",
           "gabarito_cenarios", "gabarito_registros"]

# --------------------------------------------------------------------------- parâmetros
FAIXA_PRECO = {"diesel_s10": (4.5, 9.0), "gasolina": (4.5, 9.5)}
TOLERANCIA_TANQUE = 1.05
JANELA_DUP_REG_MIN = 15
JANELA_DUP_PEDAGIO_MIN = 5
TOLERANCIA_PRECO_REFERENCIA = 0.02
ZMOD_LIMIAR = 3.5
CUSUM_K, CUSUM_H = 0.5, 4.0
SUBUTILIZACAO_LIMIAR = 0.40

# Precedência das fontes quando o mesmo fato aparece duas vezes (menor = mais confiável)
PRECEDENCIA_ORIGEM = {"api": 1, "extrato_cartao_combustivel": 2, "extrato_pedagio": 2, "csv": 3, "xlsx": 3,
                      "pdf_texto": 4, "pdf_imagem": 5, "imagem": 5, "texto_livre": 6, "digitacao_manual": 7}

# severidade, tratamento na base analítica e peso na dimensão Consistência quando pendente
REGRAS = {
    "R-DUP-ARQ": ("bloqueante", "excluir", 0.0),
    "R-DUP-REG": ("bloqueante", "excluir", 0.0),
    "R-PED-DUP": ("alta", "manter_e_gerar_achado", 0.0),
    "R-DATA-FUT": ("alta", "quarentena", 1.0),
    "R-VALOR-NEG": ("alta", "quarentena", 1.0),
    "R-CONF-EXTRACAO": ("media", "quarentena", 1.0),
    "R-VEIC-DESC": ("alta", "manter_sem_veiculo", 0.5),
    "R-COMB-INCOMP": ("alta", "manter_sem_consumo", 0.5),
    "R-ABS-TANQUE": ("alta", "manter_sem_consumo", 0.5),
    "R-CONC-VALOR": ("media", "manter_sem_consumo", 0.5),
    "R-PRECO-FAIXA": ("media", "manter_sem_consumo", 0.5),
    "R-ODO-REG": ("media", "manter_sem_odometro", 0.1),
    "R-CAMPO-AUSENTE": ("baixa", "imputar_IMP-01", 0.0),
}

# Peso de rastreabilidade por tipo de evidência (dimensão R)
PESO_EVIDENCIA = {"api": 1.0, "extrato_cartao_combustivel": 1.0, "extrato_pedagio": 1.0, "csv": 1.0, "xlsx": 1.0,
                  "pdf_texto": 1.0, "pdf_imagem": 0.8, "imagem": 0.8, "texto_livre": 0.7, "digitacao_manual": 0.5}

CATEGORIAS_CUSTO = ["COMBUSTIVEL", "MANUTENCAO", "PEDAGIO", "MULTA", "TRIBUTO", "SEGURO", "OUTROS"]


@dataclass
class Base:
    t: dict[str, pd.DataFrame]
    meta: dict
    lacunas: dict

    def __getattr__(self, nome):
        try:
            return self.t[nome]
        except KeyError as e:
            raise AttributeError(nome) from e


def carregar(pasta: Path) -> Base:
    t = {n: pd.read_csv(pasta / f"{n}.csv") for n in TABELAS}
    meta = json.loads((pasta / "metadados.json").read_text(encoding="utf-8"))
    lacunas = json.loads((pasta / "gabarito_lacunas.json").read_text(encoding="utf-8"))
    return Base(t, meta, lacunas)


def mes_int(comp: pd.Series) -> pd.Series:
    return comp.str[:4].astype(int) * 12 + comp.str[5:7].astype(int) - 1


def int_mes(n: np.ndarray | pd.Series) -> pd.Series:
    n = pd.Series(n)
    return (n // 12).astype(str) + "-" + (n % 12 + 1).map(lambda m: f"{m:02d}")


def janela(b: Base, emp: str) -> list[str]:
    ini, fim = b.meta["periodos"][emp]
    return [str(p) for p in pd.period_range(ini, fim, freq="M")]


# --------------------------------------------------------------------------- 1. validação
def validar(b: Base) -> pd.DataFrame:
    """Aplica as regras R-* e devolve uma linha por (regra, despesa)."""
    d, o = b.despesas, b.origens_dados
    linhas: list[tuple] = []

    def marcar(regra, ids, detalhe=""):
        sev, trat, _ = REGRAS[regra]
        for i in pd.Series(ids).unique():
            linhas.append((regra, sev, trat, i, detalhe))

    # R-DUP-ARQ: mesmo arquivo (hash) recebido mais de uma vez
    oo = o.sort_values("data_recebimento")
    origens_dup = oo.loc[oo.duplicated(["empresa_id", "hash_sha256"], keep="first"), "origem_id"]
    ids_dup_arq = d.loc[d.origem_id.isin(origens_dup), "despesa_id"]
    marcar("R-DUP-ARQ", ids_dup_arq, "arquivo com hash SHA-256 já recebido")

    cat = b.veiculos.merge(b.categorias_veiculo, on="categoria_id")[
        ["veiculo_id", "capacidade_tanque_l", "combustivel_padrao"]]
    ab = (b.abastecimentos
          .merge(d[["despesa_id", "veiculo_id", "origem_id", "valor_brl"]], on="despesa_id")
          .merge(o[["origem_id", "tipo_origem", "data_recebimento"]], on="origem_id")
          .merge(cat, on="veiculo_id", how="left"))
    ab = ab[~ab.despesa_id.isin(ids_dup_arq)].copy()
    ab["t"] = pd.to_datetime(ab.data_hora)

    # R-DUP-REG: mesma transação vinda de duas fontes (litros e valor iguais, até 15 min)
    ab["prec"] = ab.tipo_origem.map(PRECEDENCIA_ORIGEM).fillna(9)
    chave = ab.dropna(subset=["litros"]).assign(l=lambda x: x.litros.round(1), v=lambda x: x.valor_brl.round(0))
    dup_reg = []
    for _, g in chave.groupby(["veiculo_id", "l", "v"]):
        if len(g) < 2:
            continue
        g = g.sort_values("t").to_dict("records")
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                a, c = g[i], g[j]
                if a["origem_id"] == c["origem_id"]:
                    continue
                if abs((c["t"] - a["t"]).total_seconds()) <= JANELA_DUP_REG_MIN * 60:
                    pior = c if (c["prec"], c["data_recebimento"]) >= (a["prec"], a["data_recebimento"]) else a
                    dup_reg.append(pior["despesa_id"])
    marcar("R-DUP-REG", dup_reg, "mesma transação em duas fontes; mantida a de maior precedência")
    ab = ab[~ab.despesa_id.isin(dup_reg)]

    # R-PED-DUP: mesma praça, mesmo valor, mesmo veículo em até 5 min
    pe = b.pedagios.merge(d[["despesa_id", "veiculo_id", "valor_brl"]], on="despesa_id")
    pe = pe[pe.praca_codigo != "CONSOLIDADO_VIAGEM"].copy()
    pe["t"] = pd.to_datetime(pe.data_hora)
    pe = pe.sort_values(["veiculo_id", "praca_codigo", "valor_brl", "t"])
    pe["dt"] = pe.groupby(["veiculo_id", "praca_codigo", "valor_brl"]).t.diff()
    marcar("R-PED-DUP", pe.loc[pe.dt <= pd.Timedelta(minutes=JANELA_DUP_PEDAGIO_MIN), "despesa_id"],
           "passagem repetida na mesma praça em até 5 minutos")

    # R-ABS-TANQUE, R-COMB-INCOMP, R-PRECO-FAIXA, R-CONC-VALOR, R-CAMPO-AUSENTE
    marcar("R-ABS-TANQUE", ab.loc[ab.litros > TOLERANCIA_TANQUE * ab.capacidade_tanque_l, "despesa_id"],
           "litros acima da capacidade do tanque")
    marcar("R-COMB-INCOMP", ab.loc[ab.combustivel_padrao.notna() & (ab.combustivel != ab.combustivel_padrao),
                                   "despesa_id"], "combustível diferente do padrão da categoria")
    lo = ab.combustivel.map(lambda c: FAIXA_PRECO.get(c, (0, 1e9))[0])
    hi = ab.combustivel.map(lambda c: FAIXA_PRECO.get(c, (0, 1e9))[1])
    marcar("R-PRECO-FAIXA", ab.loc[(ab.preco_litro < lo) | (ab.preco_litro > hi), "despesa_id"],
           "preço por litro fora da faixa plausível")
    calc = ab.litros * ab.preco_litro
    tol = np.maximum(0.05, 0.005 * ab.valor_brl.abs())
    marcar("R-CONC-VALOR", ab.loc[ab.litros.notna() & ((calc - ab.valor_brl).abs() > tol), "despesa_id"],
           "litros x preço difere do valor")
    marcar("R-CAMPO-AUSENTE", ab.loc[ab.litros.isna(), "despesa_id"], "litros ausente (derivável: valor/preço)")

    # R-ODO-REG: odômetro menor que o maior já registrado para o veículo
    s = ab.dropna(subset=["odometro_km"]).sort_values(["veiculo_id", "t"])
    ant = s.groupby("veiculo_id").odometro_km.transform(lambda x: x.cummax().shift())
    marcar("R-ODO-REG", s.loc[s.odometro_km < ant, "despesa_id"], "odômetro regressivo")

    # R-DATA-FUT, R-VEIC-DESC, R-VALOR-NEG, R-CONF-EXTRACAO
    dd = d.merge(o[["origem_id", "data_recebimento"]], on="origem_id")
    marcar("R-DATA-FUT", dd.loc[pd.to_datetime(dd.data_evento) > pd.to_datetime(dd.data_recebimento), "despesa_id"],
           "data do evento posterior ao recebimento do documento")
    marcar("R-VEIC-DESC", d.loc[d.veiculo_id.notna() & ~d.veiculo_id.isin(b.veiculos.veiculo_id), "despesa_id"],
           "veículo fora do cadastro")
    marcar("R-VALOR-NEG", d.loc[(d.valor_brl < 0) & ~d.subcategoria.str.startswith("estorno"), "despesa_id"],
           "valor negativo sem identificação de estorno")
    marcar("R-CONF-EXTRACAO", d.loc[d.requer_revisao.astype(bool), "despesa_id"],
           "confiança de extração abaixo de 0,80")
    return pd.DataFrame(linhas, columns=["regra_id", "severidade", "tratamento", "despesa_id", "detalhe"])


def avaliar_regras(b: Base, problemas: pd.DataFrame) -> pd.DataFrame:
    """Compara as regras com o gabarito: cobertura dos casos injetados e marcações fora do gabarito."""
    gc, gr = b.gabarito_cenarios, b.gabarito_registros
    injetados = set(gr.registro_id)
    linhas = []
    for _, c in gc[gc.regra_ou_metodo_esperado.str.contains("R-") & (gc.tipo != "controle_negativo")].iterrows():
        regras = [r.strip() for r in c.regra_ou_metodo_esperado.replace(" e ", "+").split("+")
                  if r.strip().startswith("R-")]
        alvo = set(gr.loc[gr.cenario_id == c.cenario_id, "registro_id"])
        marcados = set(problemas.loc[problemas.regra_id.isin(regras), "despesa_id"])
        linhas.append({"cenario_id": c.cenario_id, "regras": "+".join(regras), "injetados": len(alvo),
                       "detectados": len(alvo & marcados), "cobertura": len(alvo & marcados) / max(len(alvo), 1)})
    for _, c in gc[gc.tipo == "controle_negativo"].iterrows():
        alvo = set(gr.loc[gr.cenario_id == c.cenario_id, "registro_id"])
        marcados = set(problemas.loc[problemas.regra_id != "R-CAMPO-AUSENTE", "despesa_id"])
        linhas.append({"cenario_id": c.cenario_id, "regras": "controle negativo", "injetados": len(alvo),
                       "detectados": len(alvo & marcados), "cobertura": 1 - len(alvo & marcados) / max(len(alvo), 1)})
    negativos = set(gr.loc[gr.cenario_id.isin(gc.loc[gc.tipo == "controle_negativo", "cenario_id"]), "registro_id"])
    fora = problemas[~problemas.despesa_id.isin(injetados - negativos) & (problemas.regra_id != "R-CAMPO-AUSENTE")]
    resumo = pd.DataFrame(linhas)
    resumo.attrs["marcacoes_fora_do_gabarito"] = fora.groupby("regra_id").despesa_id.nunique().to_dict()
    return resumo


# --------------------------------------------------------------------------- 2. base analítica e rateio
def base_analitica(b: Base, problemas: pd.DataFrame) -> pd.DataFrame:
    d = b.despesas.copy()
    trat = problemas.groupby("despesa_id").tratamento.agg(set)
    d["tratamentos"] = d.despesa_id.map(trat).apply(lambda x: x if isinstance(x, set) else set())
    d["excluida"] = d.tratamentos.apply(lambda x: "excluir" in x)
    d["quarentena"] = d.tratamentos.apply(lambda x: "quarentena" in x)
    d["custo_valido"] = ~d.excluida & ~d.quarentena & (d.natureza_custo == "proprio")
    d["veiculo_valido"] = d.veiculo_id.isin(b.veiculos.veiculo_id)
    d["consumo_valido"] = ~d.tratamentos.apply(lambda x: bool(x & {"manter_sem_consumo", "excluir", "quarentena"}))
    return d


def ratear_competencia(d: pd.DataFrame) -> pd.DataFrame:
    """Distribui cada despesa igualmente entre os meses de competencia_inicio a competencia_fim."""
    ini, fim = mes_int(d.competencia_inicio), mes_int(d.competencia_fim)
    n = (fim - ini + 1).to_numpy()
    rep = d.loc[d.index.repeat(n)].copy()
    desloc = rep.groupby(level=0).cumcount().to_numpy()
    rep["competencia"] = int_mes(ini.loc[rep.index].to_numpy() + desloc).to_numpy()
    rep["valor_competencia"] = (rep.valor_brl / np.repeat(n, n)).to_numpy()
    return rep.reset_index(drop=True)


# --------------------------------------------------------------------------- 3. indicadores
@dataclass
class Painel:
    empresa_id: str
    meses: list[str]
    custo_mes_veiculo: pd.DataFrame   # veiculo_id, competencia, categoria_custo, valor (com rateio de custos de frota)
    custo_total_categoria: pd.Series
    uso: pd.DataFrame
    extras: dict = field(default_factory=dict)


def montar_painel(b: Base, base: pd.DataFrame, emp: str) -> Painel:
    meses = janela(b, emp)
    rat = ratear_competencia(base[(base.empresa_id == emp) & base.custo_valido])
    rat = rat[rat.competencia.isin(meses)]
    uso = b.uso_veiculo_mensal.merge(b.veiculos[["veiculo_id", "frota_id", "categoria_id", "propriedade"]],
                                     on="veiculo_id")
    uso = uso[uso.frota_id.isin(b.frotas.loc[b.frotas.empresa_id == emp, "frota_id"]) & uso.competencia.isin(meses)]
    ativos = uso.groupby("competencia").veiculo_id.nunique()
    # custos sem veículo válido (apólice de frota, telemetria, veículo fora do cadastro) rateados por veículo·mês
    frota = rat[~rat.veiculo_valido].groupby(["competencia", "categoria_custo"]).valor_competencia.sum().reset_index()
    frota = frota.merge(uso[["competencia", "veiculo_id"]], on="competencia")
    frota["valor"] = frota.valor_competencia / frota.competencia.map(ativos)
    proprio = rat[rat.veiculo_valido].rename(columns={"valor_competencia": "valor"})
    cmv = pd.concat([proprio[["veiculo_id", "competencia", "categoria_custo", "valor"]],
                     frota[["veiculo_id", "competencia", "categoria_custo", "valor"]]], ignore_index=True)
    total_cat = rat.groupby("categoria_custo").valor_competencia.sum().reindex(CATEGORIAS_CUSTO).fillna(0.0)
    return Painel(emp, meses, cmv, total_cat, uso)


def indicadores_basicos(p: Painel) -> dict:
    """IND-01 a IND-05."""
    cto = float(p.custo_total_categoria.sum())
    vm = int(len(p.uso))
    km_obs = p.uso.dropna(subset=["km_rodados"])
    cobertura_km = len(km_obs) / vm if vm else 0.0
    custo_vm = p.custo_mes_veiculo.groupby(["veiculo_id", "competencia"]).valor.sum()
    chaves = pd.MultiIndex.from_frame(km_obs[["veiculo_id", "competencia"]])
    custo_coberto = float(custo_vm.reindex(chaves).fillna(0).sum())
    km_total = float(km_obs.km_rodados.sum())
    mensal = p.custo_mes_veiculo.groupby("competencia").valor.sum().reindex(p.meses).fillna(0.0)
    variacao = mensal.pct_change()
    ref3 = mensal.rolling(3).median().shift()
    return {
        "IND-01_custo_total_brl": cto,
        "IND-02_custo_por_veiculo_mes_brl": cto / vm if vm else None,
        "veiculos_mes": vm,
        "IND-03_custo_por_km_brl": custo_coberto / km_total if km_total else None,
        "IND-03_cobertura_km": cobertura_km,
        "km_observado": km_total,
        "IND-04_participacao": (p.custo_total_categoria / cto).round(4).to_dict() if cto else {},
        "IND-05_custo_mensal": mensal.round(2).to_dict(),
        "IND-05_variacao_mensal": variacao.round(4).to_dict(),
        "IND-05_desvio_vs_mediana_3m": ((mensal - ref3) / ref3).round(4).to_dict(),
    }


def consumo_mensal(b: Base, base: pd.DataFrame, emp: str) -> pd.DataFrame:
    """IND-07 e IND-08: rendimento (km/L) e preço médio pago por veículo e mês.

    Usa o método agregado (km do mês / litros do mês) e a imputação IMP-01 (litros = valor/preço)."""
    meses = janela(b, emp)
    ab = b.abastecimentos.merge(base[["despesa_id", "empresa_id", "veiculo_id", "valor_brl", "data_evento",
                                      "custo_valido", "consumo_valido", "veiculo_valido"]], on="despesa_id")
    ab = ab[(ab.empresa_id == emp) & ab.custo_valido & ab.consumo_valido & ab.veiculo_valido].copy()
    ab["litros"] = ab.litros.fillna(ab.valor_brl / ab.preco_litro)  # IMP-01
    ab["competencia"] = ab.data_evento.str[:7]
    ab = ab[ab.competencia.isin(meses)]
    g = ab.groupby(["veiculo_id", "competencia"]).agg(litros=("litros", "sum"), custo=("valor_brl", "sum"))
    uso = b.uso_veiculo_mensal.set_index(["veiculo_id", "competencia"]).km_rodados
    g["km"] = uso.reindex(g.index)
    g["km_l"] = g.km / g.litros
    g["preco_medio"] = g.custo / g.litros
    g = g.reset_index().merge(b.veiculos[["veiculo_id", "categoria_id"]], on="veiculo_id")
    # normalização pelo grupo de pares (mesma empresa e categoria, mesmo mês)
    g["km_l_pares"] = g.groupby(["categoria_id", "competencia"]).km_l.transform("median")
    g["razao_pares"] = g.km_l / g.km_l_pares
    return g


def zmod(x: pd.Series) -> pd.Series:
    """Escore z modificado (Iglewicz e Hoaglin, 1993): 0,6745 (x - mediana) / MAD."""
    med = x.median()
    mad = (x - med).abs().median()
    if not mad:
        return pd.Series(np.nan, index=x.index)
    return 0.6745 * (x - med) / mad


def cusum_queda(serie: pd.Series, base_meses: int = 6, sigma: float | None = None) -> tuple[pd.Series, str | None]:
    """CUSUM unilateral para queda: S_t = max(0, S_{t-1} + (mu0 - x_t)/sigma - k). Alarme quando S_t > h."""
    serie = serie.dropna()
    mu0 = serie.iloc[:base_meses].mean()
    sigma = sigma or serie.iloc[:base_meses].std(ddof=1)
    s, acum, alarme = [], 0.0, None
    for comp, x in serie.items():
        acum = max(0.0, acum + (mu0 - x) / sigma - CUSUM_K)
        s.append(acum)
        if alarme is None and acum > CUSUM_H:
            alarme = comp
    return pd.Series(s, index=serie.index), alarme


def lmdi(c_v: float, a_v: float, i_v: float, p_v: float, a_r: float, i_r: float, p_r: float) -> dict:
    """Decomposição LMDI-I aditiva de C = A x I x P (Ang, 2005). Os efeitos somam exatamente C_v - C_ref."""
    c_r = a_r * i_r * p_r
    if np.isclose(c_v, c_r):
        peso = c_v
    else:
        peso = (c_v - c_r) / (np.log(c_v) - np.log(c_r))
    ef = {"atividade": peso * np.log(a_v / a_r), "intensidade": peso * np.log(i_v / i_r),
          "preco": peso * np.log(p_v / p_r)}
    return {"custo_veiculo": c_v, "custo_referencia": c_r, "diferenca": c_v - c_r, **ef,
            "residuo": (c_v - c_r) - sum(ef.values())}


def decompor_combustivel(cons: pd.DataFrame, veiculo: str, meses: list[str]) -> dict:
    """Compara o veículo com o 'veículo típico' dos pares (medianas de km, L/km e R$/L) no mesmo período."""
    x = cons[cons.competencia.isin(meses)].dropna(subset=["km"])
    tot = x.groupby("veiculo_id").agg(km=("km", "sum"), litros=("litros", "sum"), custo=("custo", "sum"),
                                       categoria_id=("categoria_id", "first"))
    tot["i"] = tot.litros / tot.km
    tot["p"] = tot.custo / tot.litros
    alvo = tot.loc[veiculo]
    pares = tot[(tot.categoria_id == alvo.categoria_id) & (tot.index != veiculo)]
    r = lmdi(float(alvo.custo), float(alvo.km), float(alvo.i), float(alvo.p),
             float(pares.km.median()), float(pares.i.median()), float(pares.p.median()))
    r.update({"veiculo_id": veiculo, "km_veiculo": float(alvo.km), "km_ref": float(pares.km.median()),
              "km_l_veiculo": float(1 / alvo.i), "km_l_ref": float(1 / pares.i.median()),
              "preco_veiculo": float(alvo.p), "preco_ref": float(pares.p.median()), "n_pares": int(len(pares))})
    return r


# --------------------------------------------------------------------------- 4. confiabilidade
def pontuar_atualidade(dias: float, ok: int = 45, zero: int = 180) -> float:
    if dias <= ok:
        return 100.0
    if dias >= zero:
        return 0.0
    return 100.0 * (zero - dias) / (zero - ok)


def selo(minimo: float) -> str:
    if minimo >= 80:
        return "Alta"
    if minimo >= 60:
        return "Moderada"
    if minimo >= 40:
        return "Baixa"
    return "Insuficiente"


def confiabilidade(b: Base, base: pd.DataFrame, problemas: pd.DataFrame, emp: str, custo_estimado_lacunas: float,
                   data_ref: str) -> dict:
    meses = janela(b, emp)
    d = base[base.empresa_id == emp]
    rat = ratear_competencia(d[~d.excluida & (d.natureza_custo == "proprio")])
    rat = rat[rat.competencia.isin(meses)]
    observado = float(rat.valor_competencia.sum())
    # C - completude: parcela do custo total apoiada em dados observados
    comp = observado / (observado + custo_estimado_lacunas) if observado else 0.0
    # A - atualidade
    ultimo = pd.Period(rat.competencia.max(), freq="M").end_time.normalize()
    dias = (pd.Timestamp(data_ref) - ultimo).days
    atual = pontuar_atualidade(dias)
    # K - consistência: valor com pendência não resolvida, ponderado pela regra
    pend = problemas[problemas.despesa_id.isin(d.despesa_id)].copy()
    pend["peso"] = pend.regra_id.map(lambda r: REGRAS[r][2])
    peso_reg = pend.groupby("despesa_id").peso.max()
    valores = d.set_index("despesa_id").valor_brl.abs()
    base_valor = float(valores[~d.set_index("despesa_id").excluida].sum())
    pendente = float((valores.reindex(peso_reg.index) * peso_reg).sum())
    consist = 1 - pendente / base_valor if base_valor else 0.0
    # R - rastreabilidade: peso da evidência que sustenta cada real
    dv = d[~d.excluida].merge(b.origens_dados[["origem_id", "tipo_origem"]], on="origem_id")
    peso = dv.tipo_origem.map(PESO_EVIDENCIA).fillna(0.5)
    ocr_baixo = dv.confianca_extracao.notna() & (dv.confianca_extracao < 0.8) & (dv.status_valor != "CORRIGIDO")
    peso = np.where(ocr_baixo, np.minimum(peso, 0.5), peso)
    rastr = float((dv.valor_brl.abs() * peso).sum() / dv.valor_brl.abs().sum())
    # X - contexto operacional: categoria, modalidade e km em pelo menos 80% dos meses
    uso = b.uso_veiculo_mensal.merge(b.veiculos[["veiculo_id", "frota_id", "categoria_id"]], on="veiculo_id")
    uso = uso[uso.frota_id.isin(b.frotas.loc[b.frotas.empresa_id == emp, "frota_id"]) & uso.competencia.isin(meses)]
    por_v = uso.groupby("veiculo_id").agg(km_ok=("km_rodados", lambda s: s.notna().mean()),
                                          cat=("categoria_id", lambda s: s.notna().all()))
    modalidade_ok = bool(b.frotas.loc[b.frotas.empresa_id == emp, "modalidade_operacional"].notna().all())
    ctx = float(((por_v.km_ok >= 0.8).astype(float) + por_v.cat.astype(float) + float(modalidade_ok)).mean() / 3)
    dims = {"C_completude": 100 * comp, "A_atualidade": atual, "K_consistencia": 100 * consist,
            "R_rastreabilidade": 100 * rastr, "X_contexto": 100 * ctx}
    return {"dimensoes": {k: round(v, 1) for k, v in dims.items()}, "minimo": round(min(dims.values()), 1),
            "selo": selo(min(dims.values())), "dias_desde_ultimo_dado": int(dias),
            "custo_observado_brl": round(observado, 2), "custo_estimado_lacunas_brl": round(custo_estimado_lacunas, 2),
            "valor_pendente_ponderado_brl": round(pendente, 2)}


# --------------------------------------------------------------------------- 5. estimativa progressiva
PRIORI = {  # triangular (mínimo, moda, máximo) por veículo·mês; hipóteses a calibrar
    "km_mes": {"LEVE_PASSEIO": (800, 1500, 2800), "UTIL_LEVE": (900, 1800, 3200)},
    "rendimento_km_l": {"LEVE_PASSEIO": (9.0, 11.5, 13.5), "UTIL_LEVE": (7.5, 9.5, 11.5)},
    "preco_gasolina": (5.8, 6.3, 6.9),
    "manutencao_por_km": {"LEVE_PASSEIO": (0.08, 0.15, 0.30), "UTIL_LEVE": (0.10, 0.18, 0.35)},
    "pedagio_por_km_urbano": (0.0, 0.01, 0.05),
    "multas_veiculo_mes": (0.0, 15.0, 60.0),
    "valor_veiculo": {"LEVE_PASSEIO": (55_000, 80_000, 110_000), "UTIL_LEVE": (70_000, 100_000, 140_000)},
    "aliquota_ipva": (0.01, 0.03, 0.04),
    "licenciamento_ano": (100.0, 160.0, 250.0),
    "taxa_seguro_ano": (0.03, 0.05, 0.07),
    "locacao_mes": (2_500.0, 3_400.0, 4_500.0),
    "outros_veiculo_mes": (0.0, 30.0, 150.0),
}
N_SIMULACOES = 20_000


def _tri(rng, faixa, n):
    lo, mo, hi = faixa
    return rng.triangular(lo, mo, hi, n)


def estimativa_progressiva(b: Base, base: pd.DataFrame, semente: int = 7) -> dict:
    """Estimativa do custo total da EMP-A (6 meses) em quatro níveis de informação.

    Cada componente é observado (valor fixo) ou estimado por simulação de Monte Carlo com
    distribuições triangulares. Faixa apresentada: P10-P90 da simulação (não é probabilidade calibrada)."""
    emp, meses = "EMP-A", janela(b, "EMP-A")
    n_meses = len(meses)
    veic = b.veiculos[b.veiculos.frota_id == "FRO-A1"]
    proprios = veic[veic.propriedade == "propria"]
    locados = veic[veic.propriedade == "locada"]
    d = base[(base.empresa_id == emp)]
    rat = ratear_competencia(d[~d.excluida & (d.natureza_custo == "proprio")])
    rat = rat[rat.competencia.isin(meses)]
    obs = rat.groupby("subcategoria").valor_competencia.sum()
    obs_cat = rat.groupby("categoria_custo").valor_competencia.sum()
    manut_obs = float(obs_cat.get("MANUTENCAO", 0.0))
    meses_manut = sorted(set(rat.loc[rat.categoria_custo == "MANUTENCAO", "competencia"]))
    verdade = float(obs_cat.sum()) + float(b.lacunas["G29"])
    km_real = b.uso_veiculo_mensal[b.uso_veiculo_mensal.veiculo_id.isin(veic.veiculo_id)
                                   & b.uso_veiculo_mensal.competencia.isin(meses)]
    # respostas "declaradas" pelo gestor no nível 1, com erro de declaração hipotético (+8% e -5%)
    km_medio_declarado = round(1.08 * float(km_real.km_rodados.mean()), -1)
    combustivel_real_mes = float(obs_cat.get("COMBUSTIVEL", 0.0)) / n_meses
    combustivel_declarado_mes = round(0.95 * combustivel_real_mes, -2)
    rng = np.random.default_rng(semente)
    n = N_SIMULACOES

    def km_categoria(cat, nivel):
        if nivel == 0:
            return _tri(rng, PRIORI["km_mes"][cat], n)
        return km_medio_declarado * rng.triangular(0.85, 1.0, 1.15, n)

    def componentes(nivel: int, fixar: set[str] = frozenset()) -> dict[str, np.ndarray]:
        comp: dict[str, np.ndarray] = {}
        km = {c: km_categoria(c, nivel) for c in ("LEVE_PASSEIO", "UTIL_LEVE")}
        n_cat = veic.categoria_id.value_counts()
        n_prop = proprios.categoria_id.value_counts()
        # combustível
        if nivel >= 2:
            comp["combustivel"] = np.full(n, float(obs_cat.get("COMBUSTIVEL", 0.0)))
        elif nivel == 1:
            comp["combustivel"] = combustivel_declarado_mes * n_meses * rng.triangular(0.9, 1.0, 1.1, n)
        else:
            preco = _tri(rng, PRIORI["preco_gasolina"], n)
            comp["combustivel"] = sum(n_cat.get(c, 0) * km[c] / _tri(rng, PRIORI["rendimento_km_l"][c], n)
                                      for c in km) * preco * n_meses
        # pedágio e outros (estacionamento)
        if nivel >= 2:
            comp["pedagio"] = np.full(n, float(obs_cat.get("PEDAGIO", 0.0)))
            comp["outros"] = np.full(n, float(obs.get("estacionamento", 0.0)))
            comp["locacao"] = np.full(n, float(obs.get("locacao_veiculo", 0.0)))
        else:
            comp["pedagio"] = sum(n_cat.get(c, 0) * km[c] for c in km) * _tri(rng, PRIORI["pedagio_por_km_urbano"], n) * n_meses
            comp["outros"] = len(veic) * _tri(rng, PRIORI["outros_veiculo_mes"], n) * n_meses
            comp["locacao"] = len(locados) * _tri(rng, PRIORI["locacao_mes"], n) * n_meses
        # manutenção (só veículos próprios; locação inclui manutenção)
        if nivel >= 2:
            faltam = n_meses - len(meses_manut)
            media = manut_obs / max(len(meses_manut), 1)
            comp["manutencao"] = manut_obs + media * faltam * rng.triangular(0.6, 1.0, 1.6, n)
        else:
            comp["manutencao"] = sum(n_prop.get(c, 0) * km[c] * _tri(rng, PRIORI["manutencao_por_km"][c], n)
                                     for c in km) * n_meses
        # multas, tributos e seguro (próprios)
        if nivel >= 3:
            comp["multas"] = np.full(n, float(b.lacunas["G29.multas"]))
            comp["tributos"] = np.full(n, float(b.lacunas["G29.tributos"]))
            comp["seguro"] = np.full(n, float(b.lacunas["G29.seguro"]))
        else:
            comp["multas"] = len(proprios) * _tri(rng, PRIORI["multas_veiculo_mes"], n) * n_meses
            valor = {c: _tri(rng, PRIORI["valor_veiculo"][c], n) for c in km}
            ipva = sum(n_prop.get(c, 0) * valor[c] for c in km) * _tri(rng, PRIORI["aliquota_ipva"], n)
            lic = len(proprios) * _tri(rng, PRIORI["licenciamento_ano"], n)
            comp["tributos"] = (ipva + lic) * n_meses / 12
            comp["seguro"] = sum(n_prop.get(c, 0) * valor[c] for c in km) * _tri(rng, PRIORI["taxa_seguro_ano"], n) * n_meses / 12
        for k in fixar:
            comp[k] = np.full(n, float(np.median(comp[k])))
        return comp

    def resumir(comp):
        total = sum(comp.values())
        p10, p50, p90 = np.percentile(total, [10, 50, 90])
        lo, hi = float(min(total)), float(max(total))
        observado = sum(float(v[0]) for v in comp.values() if np.ptp(v) == 0)
        return {"p10": float(p10), "p50": float(p50), "p90": float(p90), "largura_p10_p90": float(p90 - p10),
                "min_simulado": lo, "max_simulado": hi, "parcela_observada": observado / float(p50),
                "contem_valor_real": bool(p10 <= verdade <= p90),
                "componentes_p50": {k: float(np.median(v)) for k, v in comp.items()}}

    niveis = {}
    descricao = {
        0: "Composição da frota (8 veículos: 4 utilitários e 2 automóveis próprios, 2 automóveis locados), segmento e UF",
        1: "+ duas respostas: km médio mensal por veículo e gasto mensal com combustível",
        2: "+ extratos de combustível e pedágio, faturas de locação e 3 meses de notas de oficina (situação atual)",
        3: "+ apólice de seguro, comprovantes de IPVA/licenciamento e relação de multas (simulação do próximo passo)",
    }
    for nivel in range(4):
        rng = np.random.default_rng(semente + nivel)
        niveis[nivel] = {"descricao": descricao[nivel], **resumir(componentes(nivel))}
    # valor da informação no nível 2: quanto cada pergunta estreita a faixa P10-P90.
    # Mesmos sorteios em todas as comparações (números aleatórios comuns).
    perguntas = [
        ("seguro", "Enviar a apólice de seguro (ou informar o prêmio anual)", 1),
        ("tributos", "Enviar comprovantes de IPVA e licenciamento (ou informar os valores pagos)", 1),
        ("multas", "Informar se houve multas no período e o valor total pago", 1),
        ("manutencao", "Enviar as notas de oficina de out/2025, nov/2025 e mar/2026", 2),
    ]
    rng = np.random.default_rng(semente + 100)
    largura = resumir(componentes(2))["largura_p10_p90"]
    voi = []
    for chave, texto, esforco in perguntas:
        rng = np.random.default_rng(semente + 100)
        nova = resumir(componentes(2, fixar={chave}))["largura_p10_p90"]
        voi.append({"componente": chave, "pergunta": texto, "esforco": esforco,
                    "reducao_largura_brl": largura - nova, "reducao_pct": (largura - nova) / largura,
                    "pontuacao": (largura - nova) / esforco})
    voi.sort(key=lambda x: -x["pontuacao"])
    return {"valor_real_brl": verdade, "meses": n_meses, "niveis": niveis, "proximas_perguntas": voi,
            "declaracoes_nivel_1": {"km_medio_mensal_declarado": km_medio_declarado,
                                    "combustivel_mensal_declarado": combustivel_declarado_mes,
                                    "km_medio_mensal_real_veiculos_com_odometro":
                                        float(km_real.km_rodados.mean())},
            "priori": PRIORI}


# --------------------------------------------------------------------------- 6. economia e priorização
@dataclass
class Oportunidade:
    id: str
    empresa_id: str
    titulo: str
    estagio: str               # observacao | anomalia | hipotese | oportunidade_validada
    bruta_anual: float         # economia bruta anual potencial (R$), positiva quando o custo atual excede a referência
    captura: tuple[float, float, float]   # fator capturável: conservador, base, otimista (hipóteses)
    implantacao: float         # custo único (R$)
    recorrente_anual: float    # custo recorrente da ação (R$/ano)
    confianca: str             # Alta | Moderada | Baixa
    urgencia: float            # 1,0 ou 1,25
    esforco_pessoa_semana: float
    viavel: bool = True
    risco: str = "baixo"
    recuperacao_pontual: float = 0.0
    evidencias: dict = field(default_factory=dict)

    def liquida(self, cenario: int) -> float:
        return self.bruta_anual * self.captura[cenario] - self.recorrente_anual


FATOR_CONFIANCA = {"Alta": 1.0, "Moderada": 0.75, "Baixa": 0.5}


def priorizar(ops: list[Oportunidade]) -> pd.DataFrame:
    """Prioridade = economia líquida anual (cenário-base) x fator de confiança x urgência / esforço."""
    linhas = []
    for o in ops:
        liq = o.liquida(1)
        p = liq * FATOR_CONFIANCA[o.confianca] * o.urgencia / o.esforco_pessoa_semana if o.viavel else np.nan
        linhas.append({"id": o.id, "titulo": o.titulo, "estagio": o.estagio, "bruta_anual": o.bruta_anual,
                       "liquida_conservador": o.liquida(0), "liquida_base": liq, "liquida_otimista": o.liquida(2),
                       "implantacao": o.implantacao, "confianca": o.confianca, "urgencia": o.urgencia,
                       "esforco": o.esforco_pessoa_semana, "risco": o.risco, "prioridade": p,
                       "recuperacao_pontual": o.recuperacao_pontual})
    df = pd.DataFrame(linhas).sort_values("prioridade", ascending=False, na_position="last")
    df["ordem"] = range(1, len(df) + 1)
    return df


# Escada de evidência: cada cenário inclui apenas os estágios listados
INCLUSAO_CENARIO = {0: {"oportunidade_validada"},
                    1: {"oportunidade_validada", "anomalia"},
                    2: {"oportunidade_validada", "anomalia", "hipotese"}}


def cenarios_portfolio(ops: list[Oportunidade], custo_programa_anual: float = 0.0) -> dict:
    """Agrega oportunidades não sobrepostas por cenário.

    conservador: só oportunidades validadas; base: + anomalias com evidência estatística;
    otimista: + hipóteses. Em cada cenário entram apenas itens com economia líquida positiva.
    Economia líquida = bruta x captura - custos recorrentes (inclui o custo de operar o plano).
    Payback = implantação / economia líquida mensal. ROI 12 meses = (líquida - implantação) /
    (implantação + custos recorrentes), isto é, sobre o custo total da iniciativa no horizonte."""
    out = {}
    for k, nome in enumerate(["conservador", "base", "otimista"]):
        sel = [o for o in ops if o.estagio in INCLUSAO_CENARIO[k] and o.liquida(k) > 0]
        bruta_cap = sum(o.bruta_anual * o.captura[k] for o in sel)
        recorrentes = sum(o.recorrente_anual for o in sel) + (custo_programa_anual if sel else 0.0)
        implantacao = sum(o.implantacao for o in sel)
        liq = bruta_cap - recorrentes
        out[nome] = {"itens": [o.id for o in sel], "bruta_capturada": bruta_cap, "custos_recorrentes": recorrentes,
                     "implantacao": implantacao, "economia_liquida_anual": liq,
                     "payback_meses": (implantacao / (liq / 12)) if liq > 0 and implantacao > 0 else None,
                     "roi_12m": ((liq - implantacao) / (implantacao + recorrentes))
                     if (implantacao + recorrentes) > 0 else None,
                     "recuperacao_pontual": sum(o.recuperacao_pontual for o in sel)}
    return out


def premio_preco(b: Base, base: pd.DataFrame, emp: str) -> pd.DataFrame:
    """IND-08: litros comprados acima da mediana mensal de preço da própria frota (+2% de tolerância)."""
    ab = b.abastecimentos.merge(base[["despesa_id", "empresa_id", "veiculo_id", "valor_brl", "data_evento",
                                      "custo_valido", "consumo_valido", "veiculo_valido"]], on="despesa_id")
    ab = ab[(ab.empresa_id == emp) & ab.custo_valido & ab.consumo_valido & ab.veiculo_valido].copy()
    ab["litros"] = ab.litros.fillna(ab.valor_brl / ab.preco_litro)
    ab["comp"] = ab.data_evento.str[:7]
    ab["mediana"] = ab.groupby(["comp", "combustivel"]).preco_litro.transform("median")
    ab["acima"] = ab.preco_litro > ab.mediana * (1 + TOLERANCIA_PRECO_REFERENCIA)
    ab["premio"] = np.where(ab.acima, ab.litros * (ab.preco_litro - ab.mediana), 0.0)
    por_v = ab.groupby("veiculo_id").agg(premio=("premio", "sum"), litros=("litros", "sum"),
                                         pct_acima=("acima", "mean"))
    por_v["premio_por_litro"] = por_v.premio / por_v.litros
    por_v["z"] = zmod(por_v.premio_por_litro)
    return por_v


def combinar_alavancas(custo: float, reducoes: list[float]) -> dict:
    """Efeito conjunto de alavancas sobre o mesmo custo: aplicação sequencial, sem dupla contagem."""
    soma_ingenua = custo * sum(reducoes)
    restante = custo
    for r in reducoes:
        restante *= (1 - r)
    combinada = custo - restante
    return {"custo": custo, "reducoes": reducoes, "soma_ingenua": soma_ingenua, "combinada": combinada,
            "dupla_contagem_evitada": soma_ingenua - combinada}

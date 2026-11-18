#!/usr/bin/env python3
"""Verificações automáticas da documentação e da entrega (Sprints 1 e 2).

Confere dados, documentação e conformidade com o template, e grava o relatório em
docs/anexos/relatorio-validacao.md. Sai com código 1 se houver alguma FALHA.

Grupos de verificação:
  1. Dicionário de dados contra os CSVs da massa sintética
  2. Regras de máquina do dicionário aplicadas aos dados; violações fora do gabarito são falhas
  3. Integridade do gabarito e dos metadados
  4. Links internos e âncoras dos documentos Markdown
  5. Estrutura das tabelas Markdown
  6. Sintaxe dos diagramas Mermaid (exige mermaid-cli; sem ele, fica como aviso)
  7. Números citados na documentação contra os resultados calculados
  8. Dados sensíveis, segredos e e-mails
  9. Arquivos duplicados, codificação e emojis fora do README
 10. Conformidade com o template FIAP e com os arquivos de links das Sprints 1 e 2
 11. Reprodutibilidade da massa sintética (opcional, --reproduzir)

Uso:
    python src/validar_entregaveis.py [--mmdc CAMINHO] [--puppeteer-config ARQUIVO.json] [--reproduzir]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from functools import lru_cache
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
README_S1 = "docs/sprint1/README-sprint1.md"  # README entregue na Sprint 1, preservado
DADOS = RAIZ / "data" / "sintetico"
IGNORAR = {".git", "node_modules", ".venv", "__pycache__", ".ipynb_checkpoints"}
COLUNAS_DICIONARIO = ["tabela", "campo", "descricao", "tipo", "unidade", "obrigatorio", "regra_validacao",
                      "regra_maquina", "origem", "sensibilidade", "exemplo", "politica_ausencia",
                      "presente_na_massa_sintetica"]

resultados: list[tuple[str, str, str, str]] = []


def registrar(grupo: str, verificacao: str, status: str, detalhe: str = "") -> None:
    resultados.append((grupo, verificacao, status, detalhe))


def arquivos(*sufixos: str) -> list[Path]:
    saida = []
    for p in sorted(RAIZ.rglob("*")):
        if p.is_file() and not (set(p.relative_to(RAIZ).parts) & IGNORAR) and p.suffix in sufixos:
            saida.append(p)
    return saida


def rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def ler_csv(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- 1 e 2. dicionário e regras

def verificar_dicionario() -> list[dict]:
    g = "1. Dicionário"
    caminho = RAIZ / "data" / "dicionario-dados.csv"
    with open(caminho, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        cab = leitor.fieldnames
        dic = list(leitor)
    registrar(g, "Colunas do dicionário", "OK" if cab == COLUNAS_DICIONARIO else "FALHA", f"{len(cab)} colunas")
    chaves = Counter((r["tabela"], r["campo"]) for r in dic)
    dup = [k for k, n in chaves.items() if n > 1]
    registrar(g, "Campos sem duplicidade", "FALHA" if dup else "OK", f"{len(dic)} campos em "
              f"{len({r['tabela'] for r in dic})} tabelas" + (f"; duplicados: {dup}" if dup else ""))
    obrigatorias = [c for c in COLUNAS_DICIONARIO if c not in ("regra_maquina",)]
    vazias = [(r["tabela"], r["campo"], c) for r in dic for c in obrigatorias if not r[c].strip()]
    registrar(g, "Atributos preenchidos (nome, descrição, tipo, unidade, obrigatoriedade, validação, origem, "
              "sensibilidade, exemplo, ausência)", "FALHA" if vazias else "OK",
              f"{len(vazias)} atributos vazios" + (f": {vazias[:5]}" if vazias else ""))
    sem_regra = [f"{r['tabela']}.{r['campo']}" for r in dic if not r["regra_maquina"].strip()]
    registrar(g, "Regra de máquina definida", "AVISO" if sem_regra else "OK",
              f"{len(sem_regra)} campos sem regra de máquina (texto livre): {', '.join(sem_regra)}" if sem_regra
              else "todos os campos")
    por_tabela = defaultdict(list)
    for r in dic:
        por_tabela[r["tabela"]].append(r)
    presentes = sorted(t for t, rs in por_tabela.items() if any(r["presente_na_massa_sintetica"] == "S" for r in rs))
    csvs = {p.stem for p in DADOS.glob("*.csv") if not p.stem.startswith("gabarito")}
    registrar(g, "Tabelas da massa sintética documentadas", "OK" if set(presentes) == csvs else "FALHA",
              f"{len(csvs)} CSVs; diferenças: {sorted(set(presentes) ^ csvs)}" if set(presentes) != csvs
              else f"{len(csvs)} CSVs, todos no dicionário")
    divergentes = []
    for t in presentes:
        cab_csv = next(csv.reader(open(DADOS / f"{t}.csv", encoding="utf-8")))
        doc = [r["campo"] for r in por_tabela[t] if r["presente_na_massa_sintetica"] == "S"]
        if cab_csv != doc:
            divergentes.append(f"{t}: CSV {cab_csv} x dicionário {doc}")
    registrar(g, "Colunas dos CSVs iguais às do dicionário (nome e ordem)", "FALHA" if divergentes else "OK",
              "; ".join(divergentes) if divergentes else f"{sum(len(por_tabela[t]) for t in presentes)} campos "
              f"documentados nas {len(presentes)} tabelas presentes")
    return dic


def esperados_do_gabarito() -> dict[str, set[str]]:
    esperado = defaultdict(set)
    for r in ler_csv(DADOS / "gabarito_registros.csv"):
        esperado[r["tabela"]].add(r["registro_id"])
    return esperado


def aplicar_regras(dic: list[dict]) -> None:
    g = "2. Regras de máquina"
    tabelas = {t: ler_csv(DADOS / f"{t}.csv") for t in {r["tabela"] for r in dic
                                                       if r["presente_na_massa_sintetica"] == "S"}}
    pk = {r["tabela"]: r["campo"] for r in dic if "pk" in r["regra_maquina"].split(";")}
    esperado = esperados_do_gabarito()
    violacoes = []  # (tabela, id, campo, regra, valor, linha)
    indices: dict[str, set[str]] = {}
    for r in dic:
        if r["presente_na_massa_sintetica"] != "S":
            continue
        t, c = r["tabela"], r["campo"]
        regras = [x for x in r["regra_maquina"].split(";") if x]
        linhas = tabelas[t]
        vistos = Counter()
        for i, linha in enumerate(linhas):
            v = linha[c]
            ident = linha.get(pk.get(t, ""), str(i))
            if v == "":
                if r["obrigatorio"] == "Sim":
                    violacoes.append((t, ident, c, "obrigatorio", v, linha))
                continue
            for regra in regras:
                nome, _, arg = regra.partition(":")
                falhou = False
                try:
                    if nome == "pk":
                        vistos[v] += 1
                        falhou = vistos[v] > 1
                    elif nome == "regex":
                        falhou = re.fullmatch(arg, v) is None
                    elif nome == "enum":
                        falhou = v not in arg.split("|")
                    elif nome == "fk":
                        tt, cc = arg.split(".")
                        if tt in tabelas:
                            if arg not in indices:
                                indices[arg] = {x[cc] for x in tabelas[tt]}
                            falhou = v not in indices[arg]
                    elif nome == "int":
                        int(v)
                    elif nome == "num":
                        float(v)
                    elif nome == "min":
                        falhou = float(v) < float(arg)
                    elif nome == "max":
                        falhou = float(v) > float(arg)
                    elif nome == "data":
                        date.fromisoformat(v)
                    elif nome == "datahora":
                        datetime.fromisoformat(v)
                    elif nome == "mes":
                        falhou = re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", v) is None
                    elif nome == "bool":
                        falhou = v not in ("True", "False")
                    elif nome == "naovazio":
                        falhou = not v.strip()
                except ValueError:
                    falhou = True
                if falhou:
                    violacoes.append((t, ident, c, nome, v, linha))

    def no_gabarito(t, ident, linha):
        if ident in esperado.get(t, set()):
            return True
        if linha.get("despesa_id") in esperado.get("despesas", set()):
            return True
        if t == "uso_veiculo_mensal" and f"{linha['veiculo_id']}|{linha['competencia']}" in esperado[t]:
            return True
        return False

    fora = [v for v in violacoes if not no_gabarito(v[0], v[1], v[5])]
    dentro = len(violacoes) - len(fora)
    total_regras = sum(len([x for x in r["regra_maquina"].split(";") if x]) for r in dic
                       if r["presente_na_massa_sintetica"] == "S")
    registrar(g, "Regras do dicionário aplicadas a todos os registros", "OK",
              f"{total_regras} regras em {sum(len(x) for x in tabelas.values())} registros")
    registrar(g, "Violações explicadas pelo gabarito (erros injetados de propósito)", "OK",
              f"{dentro} violações em registros de cenários planejados")
    registrar(g, "Violações fora do gabarito", "FALHA" if fora else "OK",
              "; ".join(f"{t}.{c}={v!r} ({regra}) em {i}" for t, i, c, regra, v, _ in fora[:10])
              if fora else "nenhuma")


# ---------------------------------------------------------------- 3. gabarito e metadados

def verificar_gabarito() -> None:
    g = "3. Gabarito"
    cen = ler_csv(DADOS / "gabarito_cenarios.csv")
    ids = [r["cenario_id"] for r in cen]
    esperado_ids = [f"G{i:02d}" for i in range(1, 35)]
    registrar(g, "Cenários G01 a G34, sem repetição", "OK" if sorted(ids) == esperado_ids else "FALHA",
              f"{len(ids)} cenários; " + ", ".join(f"{k} {v}" for k, v in Counter(r["tipo"] for r in cen).items()))
    regs = ler_csv(DADOS / "gabarito_registros.csv")
    pks = {"despesas": "despesa_id", "veiculos": "veiculo_id", "viagens": "viagem_id", "empresas": "empresa_id"}
    faltando = []
    for t, c in pks.items():
        existentes = {r[c] for r in ler_csv(DADOS / f"{t}.csv")}
        faltando += [f"{t}:{r['registro_id']}" for r in regs if r["tabela"] == t and r["registro_id"] not in existentes]
    uso = {f"{r['veiculo_id']}|{r['competencia']}" for r in ler_csv(DADOS / "uso_veiculo_mensal.csv")}
    faltando += [r["registro_id"] for r in regs if r["tabela"] == "uso_veiculo_mensal" and r["registro_id"] not in uso]
    desconhecidas = {r["tabela"] for r in regs} - set(pks) - {"uso_veiculo_mensal", "lacunas"}
    registrar(g, "Registros do gabarito existem nos dados", "FALHA" if faltando or desconhecidas else "OK",
              f"{len(regs)} referências" + (f"; ausentes: {faltando[:5]}" if faltando else "")
              + (f"; tabelas desconhecidas: {desconhecidas}" if desconhecidas else ""))
    sem_registro = sorted(set(ids) - {r["cenario_id"] for r in regs})
    registrar(g, "Cenários com registros marcados", "OK" if not sem_registro else "AVISO",
              "todos" if not sem_registro else f"sem registro individual (avaliados por método ou lacuna): "
              f"{', '.join(sem_registro)}")
    meta = json.loads((DADOS / "metadados.json").read_text(encoding="utf-8"))
    dif = {t: (n, len(ler_csv(DADOS / f"{t}.csv"))) for t, n in meta["linhas_por_tabela"].items()
           if (DADOS / f"{t}.csv").exists() and n != len(ler_csv(DADOS / f"{t}.csv"))}
    registrar(g, "Contagens de metadados.json iguais às dos CSVs", "FALHA" if dif else "OK",
              str(dif) if dif else f"{len(meta['linhas_por_tabela'])} tabelas")


# ---------------------------------------------------------------- 4 e 5. Markdown

def sem_codigo(texto: str) -> list[tuple[int, str]]:
    linhas, dentro = [], False
    for n, linha in enumerate(texto.splitlines(), 1):
        if linha.lstrip().startswith("```"):
            dentro = not dentro
            continue
        if not dentro:
            linhas.append((n, linha))
    return linhas


def slug(titulo: str) -> str:
    t = re.sub(r"<[^>]+>", "", titulo).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


@lru_cache(maxsize=None)
def ancoras(md: Path) -> set[str]:
    vistos, saida = Counter(), set()
    for _, linha in sem_codigo(md.read_text(encoding="utf-8")):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", linha)
        if m:
            s = slug(m.group(2))
            saida.add(s if vistos[s] == 0 else f"{s}-{vistos[s]}")
            vistos[s] += 1
    return saida


def verificar_markdown() -> None:
    g4, g5 = "4. Links e âncoras", "5. Tabelas Markdown"
    mds = arquivos(".md")
    padrao = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)|(?:href|src)=\"([^\"]+)\"")
    total, quebrados, externos = 0, [], set()
    for md in mds:
        for n, linha in sem_codigo(md.read_text(encoding="utf-8")):
            for m in padrao.finditer(re.sub(r"`[^`]*`", "", linha)):
                alvo = m.group(1) or m.group(2)
                if re.match(r"^(https?:|mailto:)", alvo):
                    externos.add(alvo)
                    continue
                total += 1
                caminho, _, ancora = alvo.partition("#")
                destino = (md.parent / caminho).resolve() if caminho else md
                if not destino.exists():
                    quebrados.append(f"{rel(md)}:{n} -> {alvo} (arquivo inexistente)")
                elif ancora and destino.suffix == ".md" and ancora not in ancoras(destino):
                    quebrados.append(f"{rel(md)}:{n} -> {alvo} (âncora inexistente)")
    registrar(g4, "Links internos e âncoras", "FALHA" if quebrados else "OK",
              f"{len(quebrados)} quebrados: " + "; ".join(quebrados[:10]) if quebrados else f"{total} links internos em {len(mds)} arquivos")
    registrar(g4, "Links externos", "MANUAL",
              f"{len(externos)} endereços distintos; acesso não testado neste ambiente (rede restrita)")
    erros = []
    for md in mds:
        bloco = []
        for n, linha in sem_codigo(md.read_text(encoding="utf-8")) + [(0, "")]:
            if linha.lstrip().startswith("|"):
                bloco.append((n, linha))
                continue
            if bloco:
                contagens = [(n2, len(re.split(r"(?<!\\)\|", l2.strip().strip("|")))) for n2, l2 in bloco]
                base = contagens[0][1]
                erros += [f"{rel(md)}:{n2} ({c} células, cabeçalho {base})" for n2, c in contagens if c != base]
                if len(bloco) > 1 and not re.fullmatch(r"\|?(\s*:?-+:?\s*\|)+\s*:?-*:?\s*\|?", bloco[1][1].strip()):
                    erros.append(f"{rel(md)}:{bloco[1][0]} (linha separadora inválida)")
                bloco = []
    registrar(g5, "Mesma quantidade de células em cada linha", "FALHA" if erros else "OK",
              "; ".join(erros[:10]) if erros else "todas as tabelas")


# ---------------------------------------------------------------- 6. Mermaid

def verificar_mermaid(mmdc: str | None, config: Path | None) -> None:
    g = "6. Mermaid"
    blocos = []
    for md in arquivos(".md"):
        texto = md.read_text(encoding="utf-8")
        for i, m in enumerate(re.finditer(r"```mermaid\n(.*?)```", texto, re.S), 1):
            blocos.append((f"{rel(md)}#{i}", m.group(1)))
    exe = mmdc or shutil.which("mmdc")
    if not exe:
        registrar(g, "Sintaxe dos diagramas", "AVISO", f"{len(blocos)} diagramas; mermaid-cli não encontrado, "
                  "use --mmdc para verificar")
        return
    erros = []
    with tempfile.TemporaryDirectory() as tmp:
        cfg = config or Path(tmp) / "puppeteer.json"
        if not config:
            cfg.write_text(json.dumps({"args": ["--no-sandbox"]}))
        for nome, codigo in blocos:
            entrada, saida = Path(tmp) / "d.mmd", Path(tmp) / "d.svg"
            entrada.write_text(codigo, encoding="utf-8")
            r = subprocess.run([exe, "-i", str(entrada), "-o", str(saida), "-p", str(cfg), "-q"],
                               capture_output=True, text=True)
            if r.returncode != 0:
                erros.append(f"{nome}: {(r.stderr or r.stdout).strip().splitlines()[-1:]}")
    registrar(g, "Sintaxe dos diagramas (renderização com mermaid-cli)", "FALHA" if erros else "OK",
              "; ".join(erros) if erros else f"{len(blocos)} diagramas renderizados sem erro")


# ---------------------------------------------------------------- 7. números citados

def br(v: float, casas: int = 2) -> str:
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + s


def verificar_numeros() -> None:
    g = "7. Números citados"
    R = json.loads((RAIZ / "data" / "resultados" / "exemplos-calculados.json").read_text(encoding="utf-8"))
    est = R["estimativa_EMP-A"]["niveis"]
    cen_c, cen_b = R["oportunidades"]["EMP-C"]["cenarios"], R["oportunidades"]["EMP-B"]["cenarios"]
    ind = R["indicadores"]
    mil = lambda v: f"R$ {round(v / 1000):d} mil"  # noqa: E731
    afirmacoes = [
        (README_S1, f"{mil(est['0']['p10'])} a {mil(est['0']['p90'])}", "faixa N0 da EMP-A"),
        (README_S1, f"cerca de R$ {round(cen_c['base']['economia_liquida_anual'] / 1000):d} mil", "cenário-base EMP-C"),
        ("docs/anexos/exemplos-calculados.md", br(ind["EMP-B"]["IND-01_custo_total_brl"]), "IND-01 EMP-B"),
        ("docs/anexos/exemplos-calculados.md", br(ind["EMP-C"]["IND-01_custo_total_brl"]), "IND-01 EMP-C"),
        ("docs/anexos/exemplos-calculados.md", br(R["valor_real_brl"] if "valor_real_brl" in R else
                                                   R["estimativa_EMP-A"]["valor_real_brl"]), "valor real EMP-A"),
        ("docs/diagnostico.md", br(R["estimativa_EMP-A"]["valor_real_brl"]), "valor real EMP-A no diagnóstico"),
        ("docs/economia-recomendacoes.md", br(cen_c["base"]["economia_liquida_anual"], 0), "cenário-base EMP-C"),
        ("docs/economia-recomendacoes.md", f"-R$ {br(-cen_b['base']['economia_liquida_anual'], 0)}",
         "cenário-base EMP-B"),
        ("docs/economia-recomendacoes.md", br(cen_c["conservador"]["economia_liquida_anual"], 0), "conservador EMP-C"),
        ("docs/economia-recomendacoes.md", br(cen_c["otimista"]["economia_liquida_anual"], 0), "otimista EMP-C"),
    ]
    sem_bater = []
    for arq, texto, nome in afirmacoes:
        conteudo = (RAIZ / arq).read_text(encoding="utf-8")
        if texto not in conteudo:
            sem_bater.append(f"{nome}: '{texto}' não encontrado em {arq}")
    registrar(g, "Valores-chave da documentação iguais aos calculados", "FALHA" if sem_bater else "OK",
              "; ".join(sem_bater) if sem_bater else f"{len(afirmacoes)} afirmações conferidas")
    # Valores em reais com centavos citados nos documentos escritos à mão devem existir no anexo calculado
    anexo = (RAIZ / "docs" / "anexos" / "exemplos-calculados.md").read_text(encoding="utf-8")
    hip = json.dumps(R, ensure_ascii=False) + (DADOS / "gabarito_lacunas.json").read_text(encoding="utf-8")
    numeros_anexo = set(re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}", anexo))
    soltos = []
    for md in arquivos(".md"):
        if ("anexos" in md.parts or "sprint2" in md.parts or "outputs" in md.parts or md.name == "README.md"
                or md.name in ("referencias.md", "validacao.md", "teste-adversarial.md")):
            continue  # a Sprint 2 é conferida contra as saídas do pipeline em verificar_sprint2()
        for _, linha in sem_codigo(md.read_text(encoding="utf-8")):
            for n in re.findall(r"R\$ ?(\d{1,3}(?:\.\d{3})+,\d{2})", linha):
                if n == "1.234,56":  # exemplo de formatação em ux-identidade-visual.md
                    continue
                if n not in numeros_anexo and n.replace(".", "").replace(",", ".") not in hip:
                    soltos.append(f"{rel(md)}: R$ {n}")
    registrar(g, "Valores monetários com centavos encontrados no anexo calculado",
              "AVISO" if soltos else "OK",
              ("não localizados (conferir manualmente): " + "; ".join(sorted(set(soltos))[:15])) if soltos
              else "todos localizados")


# ---------------------------------------------------------------- 8. dados sensíveis

def verificar_sensiveis() -> None:
    g = "8. Dados sensíveis"
    padroes = {
        "CPF formatado": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
        "CNPJ formatado": r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
        "Placa real (antiga ou Mercosul)": r"\b(?!(?:" + "|".join(PREFIXOS_INTERNOS) + r")-)[A-Z]{3}-?\d[A-Z0-9]\d{2}\b",
        "Chave privada": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "Token AWS": r"\bAKIA[0-9A-Z]{16}\b",
        "Token GitHub": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
        "Chave de API genérica": r"\bsk-[A-Za-z0-9]{20,}\b",
        "Senha em texto": r"(?i)\b(password|senha)\s*[:=]\s*['\"][^'\"]{4,}['\"]",
    }
    permitidos_email = {"noreply@anthropic.com"}
    achados = defaultdict(list)
    alvos = arquivos(".md", ".csv", ".json", ".py", ".txt", ".html", ".css", ".svg", ".mmd")
    for p in alvos:
        texto = p.read_text(encoding="utf-8", errors="replace")
        for nome, rx in padroes.items():
            for m in re.finditer(rx, texto):
                achados[nome].append(f"{rel(p)}: {m.group(0)[:20]}")
        for m in re.finditer(r"[\w.+-]+@[\w-]+\.[\w.]+", texto):
            if m.group(0) not in permitidos_email and not m.group(0).endswith((".png", ".svg")):
                achados["E-mail"].append(f"{rel(p)}: {m.group(0)}")
    for nome in list(padroes) + ["E-mail"]:
        registrar(g, nome, "FALHA" if achados[nome] else "OK",
                  "; ".join(achados[nome][:5]) if achados[nome] else f"nenhuma ocorrência em {len(alvos)} arquivos")


# ---------------------------------------------------------------- 9. arquivos

# Prefixos de identificadores internos e fictícios (ex.: USR-0001), que têm o formato de placa antiga
PREFIXOS_INTERNOS = ("CNS", "MED", "PRM", "REF", "USR", "EMP", "FRO", "DSP", "ORI", "VGM", "DGN", "ACH", "REC", "CEN")

EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u203C\u2049\uFE0F]")


def verificar_arquivos() -> None:
    g = "9. Arquivos"
    hashes = defaultdict(list)
    for p in sorted(RAIZ.rglob("*")):
        if (p.is_file() and not (set(p.relative_to(RAIZ).parts) & IGNORAR) and p.stat().st_size > 0
                and p.name != ".gitignore"):
            hashes[hashlib.sha256(p.read_bytes()).hexdigest()].append(rel(p))
    dup = [v for v in hashes.values() if len(v) > 1]
    registrar(g, "Arquivos duplicados (mesmo conteúdo)", "AVISO" if dup else "OK",
              "; ".join(" = ".join(v) for v in dup) if dup else f"{sum(len(v) for v in hashes.values())} arquivos")
    invalidos = []
    for p in arquivos(".md", ".csv", ".json", ".py", ".txt", ".html", ".css"):
        try:
            p.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            invalidos.append(rel(p))
    registrar(g, "Codificação UTF-8", "FALHA" if invalidos else "OK", ", ".join(invalidos) or "todos os textos")
    com_emoji = [rel(p) for p in arquivos(".md", ".html", ".svg") if not p.name.startswith("README")
                 and EMOJI.search(p.read_text(encoding="utf-8"))]
    registrar(g, "Sem emojis fora dos títulos do template", "FALHA" if com_emoji else "OK",
              ", ".join(com_emoji) or "nenhum")
    pend = Counter()
    for p in arquivos(".md", ".txt"):
        if p.name == "relatorio-validacao.md":
            continue
        n = len(re.findall(r"\[Pendência|PENDENTE", p.read_text(encoding="utf-8")))
        if n:
            pend[rel(p)] = n
    registrar(g, "Pendências declaradas no texto", "INFO",
              f"{sum(pend.values())} marcações: " + ", ".join(f"{k} ({v})" for k, v in pend.most_common()))


# ---------------------------------------------------------------- 10. template e entrega

def verificar_links_txt(g: str, nome: str) -> None:
    txt = RAIZ / nome
    if not txt.exists():
        registrar(g, f"{nome}", "FALHA", "inexistente")
        return
    linhas = [x for x in txt.read_text(encoding="utf-8").splitlines() if x.strip()]
    repo_ok = any("https://github.com/fabrizzioriccelli/1TIAO-ENTERPRISE-CHALLENGE-" in x for x in linhas)
    video = [x for x in linhas if x.lower().startswith("vídeo")]
    video_ok = bool(video) and (("youtube.com/" in video[0] or "youtu.be/" in video[0]) or "PENDENTE" in video[0])
    registrar(g, f"{nome}: só repositório e vídeo", "OK" if repo_ok and video_ok and len(linhas) == 2
              else "FALHA", f"{len(linhas)} linhas")
    registrar(g, f"{nome}: link do vídeo", "PENDENTE" if video and "PENDENTE" in video[0] else "MANUAL",
              "vídeo não publicado" if video and "PENDENTE" in video[0] else "testar em janela anônima")


def verificar_template() -> None:
    g = "10. Template e entrega"
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    # "Nome do grupo" é opcional: o grupo não adotou nome e removeu a seção do README
    registrar(g, "Seção Nome do grupo", "INFO", "presente" if "## Nome do grupo" in readme
              else "removida pelo grupo, que não adotou nome")
    registrar(g, "Título do template 1TIAO", "OK" if re.search(r"^# ENTERPRISE CHALLENGE - \S", readme, re.M)
              else "FALHA")
    secoes = ["## 👨‍🎓 Integrantes", "## 👩‍🏫 Professores", "### Tutor(a)", "### Coordenador(a)",
              "## 📜 Descrição", "## 📁 Estrutura de pastas", "## 📎 Links e Observações", "### Listagem de Links",
              "### Explicação de decisões técnicas", "### Observações Gerais", "### Detalhamento da ideia",
              "### Avanços e ajustes", "## 🔧 Como executar o código", "## 🗃 Histórico de lançamentos",
              "## 📋 Licença"]
    faltam = [s for s in secoes if s not in readme]
    registrar(g, "Seções do README do template", "FALHA" if faltam else "OK",
              f"faltam: {faltam}" if faltam else f"{len(secoes)} seções presentes")
    descricao = readme.split("## 📜 Descrição")[1].split("## 📁")[0]
    palavras = len(re.findall(r"\w+", re.sub(r"\]\([^)]*\)", "]", descricao)))
    registrar(g, "Descrição com até 600 palavras", "OK" if palavras <= 600 else "FALHA", f"{palavras} palavras")
    registrar(g, "Licença do template 2026", "OK" if "SabrinaOtoni/TEMPLATE-FIAP-GRAD-ON-IA" in readme else "FALHA")
    registrar(g, "Observação do tutor removida", "FALHA" if "OBSERVAÇÃO DO TUTOR" in readme else "OK")
    registrar(g, "Campo FIAP NEXT presente", "OK" if "Participação na Competição" in readme else "FALHA")
    marcado = re.search(r"\[[xX]\] (Sim, aceitamos|Não vamos)", readme)
    registrar(g, "Decisão FIAP NEXT marcada", "OK" if marcado else "PENDENTE", "depende do grupo")
    rms = re.findall(r"RM \d{6}", readme.split("## 👩‍🏫")[0])
    registrar(g, "Integrantes com RM", "OK" if len(rms) == 5 else "FALHA", f"{len(rms)} integrantes")
    registrar(g, "Logo do template", "OK" if (RAIZ / "assets" / "logo-fiap.png").exists() else "FALHA")
    pastas = [p for p in ("data", "docs", "src") if not (RAIZ / p).is_dir()]
    registrar(g, "Pastas do template", "FALHA" if pastas else "OK", f"faltam {pastas}" if pastas else "")
    registrar(g, "Link do Wokwi no README", "OK" if "wokwi.com/projects/" in readme else "PENDENTE",
              "depende do grupo salvar o projeto no wokwi.com")

    # README da Sprint 1, preservado em docs/sprint1
    s1 = (RAIZ / README_S1).read_text(encoding="utf-8")
    itens_enunciado = ["O problema e o entendimento do desafio", "Usuários e necessidades", "Solução proposta",
                       "User Stories selecionadas", "Estruturação dos dados", "Estratégia de entrada de dados",
                       "Diagnóstico dos custos", "Recomendações e plano de ação", "Tratamento de dados incompletos",
                       "Orientação ao usuário", "Arquitetura da solução", "Segurança e dados do cliente",
                       "Planejamento das próximas etapas"]
    faltam = [i for i in itens_enunciado if not re.search(r"^### \d+\. " + re.escape(i), s1, re.M)]
    registrar(g, "README da Sprint 1 preservado com os itens do enunciado", "FALHA" if faltam else "OK",
              f"faltam: {faltam}" if faltam else f"{len(itens_enunciado)} seções em {README_S1}")
    ids_us = set(re.findall(r"^\| (US-(?:GF|CF|SP)-\d{2}) \|", s1, re.M))
    registrar(g, "README da Sprint 1 explica cada User Story", "OK" if len(ids_us) == 20 else "FALHA",
              f"{len(ids_us)} de 20 User Stories na tabela")
    verificar_links_txt(g, "ENTREGA_SPRINT1_LINKS.txt")
    verificar_links_txt(g, "ENTREGA_SPRINT2_LINKS.txt")


def verificar_sprint2() -> None:
    """Números citados no README e em docs/sprint2 contra as saídas gravadas pelo pipeline."""
    g = "12. Sprint 2"
    saidas = RAIZ / "outputs"
    obrig = ["reports/relatorio_qualidade.csv", "reports/indicadores_e_diagnostico_veiculo.csv",
             "reports/benchmark_grupos.csv", "reports/comparacao_regras_ml.csv", "predictions/metricas_modelo.json",
             "predictions/previsoes_veiculo_mes.csv", "reports/resultados_sprint2.md"]
    faltam = [o for o in obrig if not (saidas / o).exists()]
    registrar(g, "Saídas do pipeline presentes", "FALHA" if faltam else "OK",
              f"faltam: {faltam}" if faltam else f"{len(obrig)} arquivos")
    if faltam:
        return
    m = json.loads((saidas / "predictions" / "metricas_modelo.json").read_text(encoding="utf-8"))
    teste = m["comparacao_modelos"]["arvore_decisao"]["teste"]
    qualidade = ler_csv(saidas / "reports" / "relatorio_qualidade.csv")
    niveis = Counter(r["nivel_regras"] for r in ler_csv(saidas / "reports" / "indicadores_e_diagnostico_veiculo.csv"))
    comp = ler_csv(saidas / "reports" / "comparacao_regras_ml.csv")
    concordam = sum(r["concordam"] in ("True", "1", "true") for r in comp)
    pct = lambda v: br(v * 100, 1) + "%"  # noqa: E731
    afirmacoes = [
        ("README.md", f"{br(len(qualidade), 0)} ocorrências", "ocorrências de qualidade"),
        ("README.md", f"{niveis['Eficiente']} veículos eficientes, {niveis['Atenção']} em atenção, "
                      f"{niveis['Ineficiente']} ineficientes e {niveis['Sem referência']} sem referência", "níveis"),
        ("README.md", f"Acurácia {pct(teste['acuracia'])} (linha de base {pct(m['linha_de_base_teste'])})", "acurácia"),
        ("README.md", f"recall {pct(teste['recall_ineficiente'])}", "recall"),
        ("README.md", f"concordam em {concordam} de {len(comp)} veículos", "regras x modelo"),
        ("docs/sprint2/machine-learning.md", pct(teste["acuracia"]), "acurácia no documento do modelo"),
    ]
    sem_bater = [f"{n}: '{t}' não encontrado em {a}" for a, t, n in afirmacoes
                 if t not in (RAIZ / a).read_text(encoding="utf-8")]
    registrar(g, "Números da Sprint 2 iguais às saídas do pipeline", "FALHA" if sem_bater else "OK",
              "; ".join(sem_bater) if sem_bater else f"{len(afirmacoes)} afirmações conferidas")


# ---------------------------------------------------------------- 11. reprodutibilidade

def verificar_reproducao() -> None:
    g = "11. Reprodutibilidade"
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([sys.executable, str(RAIZ / "src" / "gerar_dados_sinteticos.py"), "--saida", tmp],
                           capture_output=True, text=True)
        if r.returncode != 0:
            registrar(g, "Regenerar a massa sintética", "FALHA", r.stderr[-300:])
            return
        diferentes = [p.name for p in sorted(DADOS.iterdir()) if p.is_file()
                      and (Path(tmp) / p.name).read_bytes() != p.read_bytes()]
    registrar(g, "Massa regenerada idêntica à versionada", "FALHA" if diferentes else "OK",
              ", ".join(diferentes) if diferentes else f"{len(list(DADOS.iterdir()))} arquivos idênticos byte a byte")


# ---------------------------------------------------------------- relatório

def relatorio(caminho: Path) -> None:
    cont = Counter(s for _, _, s, _ in resultados)
    linhas = ["# Relatório de validação automática", "",
              "Gerado por [`src/validar_entregaveis.py`](../../src/validar_entregaveis.py). Não edite à mão: "
              "execute o script de novo.", "",
              "Status: **OK** passou; **FALHA** precisa de correção; **AVISO** revisar; **PENDENTE** depende do "
              "grupo ou de ação externa; **MANUAL** exige conferência humana; **INFO** apenas registro.", "",
              "| Status | Quantidade |", "|---|---|"]
    linhas += [f"| {s} | {cont[s]} |" for s in ("OK", "FALHA", "AVISO", "PENDENTE", "MANUAL", "INFO") if cont[s]]
    linhas += ["", "| Grupo | Verificação | Status | Detalhe |", "|---|---|---|---|"]
    for g, v, s, d in resultados:
        d = d.replace("|", "\\|").replace("\n", " ")
        linhas.append(f"| {g} | {v} | **{s}** | {d} |")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mmdc", help="caminho do executável do mermaid-cli")
    ap.add_argument("--puppeteer-config", type=Path, help="configuração do navegador usado pelo mermaid-cli")
    ap.add_argument("--reproduzir", action="store_true", help="regenera a massa sintética e compara")
    ap.add_argument("--relatorio", type=Path, default=RAIZ / "docs" / "anexos" / "relatorio-validacao.md")
    a = ap.parse_args()
    dic = verificar_dicionario()
    aplicar_regras(dic)
    verificar_gabarito()
    verificar_markdown()
    verificar_mermaid(a.mmdc, a.puppeteer_config)
    verificar_numeros()
    verificar_sensiveis()
    verificar_arquivos()
    verificar_template()
    verificar_sprint2()
    if a.reproduzir:
        verificar_reproducao()
    relatorio(a.relatorio)
    for g, v, s, d in resultados:
        print(f"[{s:8}] {g} | {v}" + (f" | {d[:160]}" if s not in ("OK",) else ""))
    cont = Counter(s for _, _, s, _ in resultados)
    print("\nResumo:", dict(cont))
    return 1 if cont["FALHA"] else 0


if __name__ == "__main__":
    sys.exit(main())

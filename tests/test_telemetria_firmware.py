import shutil
import subprocess

import pandas as pd
import pytest

from frota_pulse.config import LIMITES_TELEMETRIA, RAIZ

ESP32 = RAIZ / "src" / "esp32"


@pytest.fixture(scope="module")
def leituras():
    t = pd.read_csv(RAIZ / "data" / "telemetria" / "telemetria_esp32.csv", keep_default_na=False)
    cad = pd.read_csv(RAIZ / "data" / "raw" / "cadastro" / "cadastro_frota.csv").drop_duplicates("codigo_veiculo")
    return t.merge(cad[["codigo_veiculo", "porte", "modalidade_operacional"]], left_on="veiculo_id",
                   right_on="codigo_veiculo")


def test_alertas_do_firmware_batem_com_os_limites_do_python(leituras):
    for classe, lim in LIMITES_TELEMETRIA.items():
        t = leituras[leituras.porte == classe]
        assert (t.temperatura_c > lim["temp_limite"]).eq(t.alertas.str.contains("TEMP_ALTA")).all()
        assert (t.rpm > lim["rpm_limite"]).eq(t.alertas.str.contains("RPM_ALTO")).all()
        assert (t.nivel_combustivel_pct < lim["comb_min"]).eq(t.alertas.str.contains("COMB_BAIXO")).all()
        urb = t.modalidade_operacional.eq("urbana_servicos")
        vlim = urb.map({True: lim["vel_max_urbana"], False: lim["vel_max_rodovia"]})
        assert (t.velocidade_kmh > vlim).eq(t.alertas.str.contains("VEL_EXCESSO")).all()


def test_ha_leituras_normais_e_anormais(leituras):
    assert {"NORMAL", "ATENCAO", "CRITICO"} <= set(leituras.status)


@pytest.mark.skipif(shutil.which("g++") is None, reason="g++ não disponível")
def test_firmware_compila_e_gera_a_mesma_telemetria(tmp_path):
    exe = tmp_path / "t"
    subprocess.run(["g++", "-std=c++17", "-O2", "-DNATIVO", "-DMODO_LOTE", "-I", str(ESP32 / "nativo"), "-I",
                    str(ESP32 / "firmware" / "telemetria_frota"), "-x", "c++",
                    str(ESP32 / "firmware" / "telemetria_frota" / "telemetria_frota.ino"), "-x", "none",
                    str(ESP32 / "nativo" / "main.cpp"), "-o", str(exe)], check=True)
    saida = subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout
    assert saida == (RAIZ / "data" / "telemetria" / "telemetria_esp32.csv").read_text(encoding="utf-8")

# Anexo — exemplos calculados

> Gerado automaticamente por `src/exemplos_calculados.py` a partir de `data/sintetico/` (dados **fictícios**).
> Não edite à mão: rode o script novamente. Os números servem para verificar fórmulas e regras; não descrevem nenhuma frota real e não são promessa de economia.

Data de referência da análise: **2026-07-10**.

## 1. Regras de qualidade aplicadas aos cenários injetados

Cobertura = registros injetados detectados pela regra esperada. Nos controles negativos, 100% significa que nenhum registro legítimo foi marcado.

| Cenário | Regra(s) | Injetados | Detectados | Cobertura |
|---|---|---|---|---|
| G01 | R-DUP-ARQ | 161 | 161 | 100% |
| G02 | R-PED-DUP | 15 | 15 | 100% |
| G10 | R-CAMPO-AUSENTE | 20 | 20 | 100% |
| G11 | R-DUP-REG | 40 | 40 | 100% |
| G14 | R-ABS-TANQUE+R-CONC-VALOR | 5 | 5 | 100% |
| G15 | R-ODO-REG | 6 | 6 | 100% |
| G16 | R-DATA-FUT | 2 | 2 | 100% |
| G17 | R-PRECO-FAIXA+R-CONC-VALOR | 3 | 3 | 100% |
| G18 | R-VEIC-DESC | 4 | 4 | 100% |
| G19 | R-COMB-INCOMP | 2 | 2 | 100% |
| G20 | R-VALOR-NEG | 1 | 1 | 100% |
| G32 | R-CONF-EXTRACAO | 50 | 50 | 100% |
| G28 | R-CONF-EXTRACAO | 2 | 2 | 100% |
| G33 | controle negativo | 2 | 0 | 100% |
| G34 | controle negativo | 2 | 0 | 100% |

Marcações fora do gabarito: **0**. Limitação: as regras foram escritas conhecendo os erros injetados; este teste comprova a mecânica, não o desempenho em dados reais.

| Empresa | Excluído por duplicidade | Em quarentena |
|---|---|---|
| EMP-A | R$ 0,00 | R$ 3.313,84 |
| EMP-B | R$ 110.539,04 | R$ 0,00 |
| EMP-C | R$ 82.171,57 | R$ 25.156,49 |

Sem a regra R-DUP-ARQ, o combustível da EMP-B apareceria 8,2% maior (R$ 110.539,04), um desvio inexistente.

## 2. Indicadores básicos (custo por competência, dentro da janela de cada empresa)

| Empresa | IND-01 Custo total | Veículos·mês | IND-02 R$/veículo·mês | IND-03 R$/km | Cobertura de km | km observados |
|---|---|---|---|---|---|---|
| EMP-A | R$ 102.812,07 | 48 | R$ 2.141,92 | R$ 1,491 | 62,5% | 50.363 |
| EMP-B | R$ 2.334.087,68 | 360 | R$ 6.483,58 | R$ 1,974 | 99,2% | 1.168.719 |
| EMP-C | R$ 16.583.488,63 | 480 | R$ 34.548,93 | R$ 3,437 | 100,0% | 4.825.288 |

Participação por categoria (IND-04):

| Empresa | COMBUSTIVEL | MANUTENCAO | PEDAGIO | MULTA | TRIBUTO | SEGURO | OUTROS |
|---|---|---|---|---|---|---|---|
| EMP-A | 54,1% | 1,5% | 3,2% | 0,0% | 0,0% | 0,0% | 41,1% |
| EMP-B | 57,9% | 20,7% | 8,3% | 0,3% | 3,4% | 8,5% | 1,0% |
| EMP-C | 69,4% | 20,3% | 4,7% | 0,0% | 1,6% | 3,6% | 0,3% |

### Caixa x competência (EMP-B)

A renovação do seguro paga à vista em abr/2026 cria um pico de caixa que não é aumento de custo.

| Mês | Caixa | Competência |
|---|---|---|
| 2025-07 | R$ 166.652,97 | R$ 189.621,48 |
| 2025-08 | R$ 178.651,37 | R$ 201.619,88 |
| 2025-09 | R$ 153.808,93 | R$ 176.777,44 |
| 2025-10 | R$ 175.875,88 | R$ 198.844,39 |
| 2025-11 | R$ 193.882,01 | R$ 216.850,52 |
| 2025-12 | R$ 176.201,07 | R$ 199.169,58 |
| 2026-01 | R$ 169.649,17 | R$ 168.459,43 |
| 2026-02 | R$ 186.850,94 | R$ 185.661,20 |
| 2026-03 | R$ 178.460,32 | R$ 177.270,58 |
| 2026-04 | R$ 369.725,51 | R$ 182.167,09 |
| 2026-05 | R$ 189.353,42 | R$ 212.879,48 |
| 2026-06 | R$ 201.240,51 | R$ 224.766,57 |

## 3. Rendimento e mudança persistente (EMP-C)

Desvio-padrão intra-veículo da razão km/L ÷ mediana dos pares na linha de base (jul-dez/2025): CAM_TRUCK 0,0291, CAV_SEMI 0,0290. CUSUM com k = 0,5 e h = 5,0.

| Veículo | Alarme | km/L base | km/L jan-jun/26 | Litros em excesso | Custo em excesso |
|---|---|---|---|---|---|
| C-V07 | 2026-02 | 2,35 | 2,02 | 4.538 | R$ 27.843,77 |
| C-V15 | 2026-02 | 2,51 | 2,25 | 2.384 | R$ 14.475,03 |
| C-V22 | 2026-03 | 2,27 | 2,09 | 1.928 | R$ 11.721,32 |

### Decomposição LMDI do custo de combustível

C = km × (L/km) × (R$/L). Os três efeitos somam exatamente a diferença (resíduo zero).

| Comparação | Custo | Referência | Diferença | Atividade (km) | Intensidade (L/km) | Preço (R$/L) | Resíduo |
|---|---|---|---|---|---|---|---|
| temporal C-V07 | R$ 221.348,86 | R$ 199.582,79 | R$ 21.766,07 | -R$ 10.726,06 | R$ 31.011,88 | R$ 1.480,24 | R$ 0,00 |
| temporal C-V01 | R$ 204.386,10 | R$ 211.240,80 | -R$ 6.854,70 | -R$ 4.936,98 | -R$ 5.172,22 | R$ 3.254,50 | -R$ 0,00 |
| pares C-V01 | R$ 204.386,10 | R$ 167.392,32 | R$ 36.993,78 | R$ 73.378,83 | -R$ 36.319,41 | -R$ 65,64 | -R$ 0,00 |
| pares C-V03 | R$ 201.810,32 | R$ 167.192,91 | R$ 34.617,41 | R$ 12.292,74 | R$ 15.635,50 | R$ 6.689,17 | R$ 0,00 |
| pares C-V07 | R$ 221.348,86 | R$ 167.252,15 | R$ 54.096,71 | R$ 21.865,24 | R$ 32.439,40 | -R$ 207,93 | R$ 0,00 |

### Preço pago acima da referência interna (EMP-C)

Prêmio total pago acima da mediana mensal da frota (+2%): **R$ 135.163,67** em 12 meses (EMP-B: R$ 2.954,27).

| Veículo | Prêmio | R$/L de prêmio | % abastecimentos acima | z modificado |
|---|---|---|---|---|
| C-V27 | R$ 17.112,86 | 0,2988 | 58,3% | 8,71 |
| C-V03 | R$ 16.183,53 | 0,2574 | 52,9% | 7,36 |
| C-V09 | R$ 15.138,72 | 0,2674 | 56,0% | 7,68 |
| C-V18 | R$ 14.412,16 | 0,3021 | 54,2% | 8,82 |
| C-V02 | R$ 13.400,65 | 0,1552 | 52,6% | 4,01 |
| C-V24 | R$ 12.723,43 | 0,2900 | 57,6% | 8,42 |
| C-V23 | R$ 3.908,34 | 0,0838 | 18,3% | 1,68 |
| C-V19 | R$ 3.526,86 | 0,0575 | 28,2% | 0,82 |

## 4. Manutenção e utilização (EMP-B)

Mediana de corretiva por km dos caminhões toco 2017-2022: R$ 0,1166/km (39,6% do gasto preventivo+corretivo).

| Veículo | Ano | km | Corretiva | Preventiva | % corretiva | Corretiva/km |
|---|---|---|---|---|---|---|
| B-V11 | 2012 | 64.319 | R$ 26.052,06 | R$ 8.078,70 | 76,3% | R$ 0,4050 |
| B-V12 | 2013 | 45.981 | R$ 23.442,08 | R$ 4.687,23 | 83,3% | R$ 0,5098 |
| B-V13 | 2012 | 49.963 | R$ 8.870,05 | R$ 10.606,25 | 45,5% | R$ 0,1775 |
| B-V14 | 2013 | 41.846 | R$ 2.962,98 | R$ 7.724,70 | 27,7% | R$ 0,0708 |

Excesso de corretiva dos quatro caminhões antigos em relação à mediana: **R$ 39.672,05**.

| Veículo | km/mês | Razão vs pares | Tributos | Seguro rateado | Custo fixo anual |
|---|---|---|---|---|---|
| B-V28 | 319 | 15,1% | R$ 1.582,89 | R$ 2.986,43 | R$ 4.569,32 |
| B-V29 | 359 | 17,0% | R$ 1.482,92 | R$ 2.776,65 | R$ 4.259,57 |
| B-V30 | 491 | 23,2% | R$ 1.803,72 | R$ 3.449,93 | R$ 5.253,65 |

Mediana de km/mês dos utilitários: 2.117 km; limiar de subutilização: 40% da mediana.

## 5. Multas e pedágio

| Empresa | Multas originais | Por 10 mil km | NIC (qtd) | NIC (valor pago) | Sem desconto (qtd) | Desconto perdido |
|---|---|---|---|---|---|---|
| EMP-B | 34 | 0,29 | 6 | R$ 2.033,43 | 7 | R$ 206,53 |
| EMP-C | 30 | 0,06 | 2 | R$ 520,63 | 1 | R$ 39,05 |

EMP-B: 15 passagens duplicadas (R$ 315,49); pedágio de R$ 0,166/km.

EMP-C: 176 retornos vazios com eixo suspenso cobrado (sobrecobrança de R$ 30.662,59); 267 viagens de lotação sem Vale-Pedágio com pedágio pago pela transportadora (R$ 137.933,94); pedágio custeado por terceiros (excluído do custo próprio): R$ 876.819,54.

Estimativa de lacunas com dados de contexto (viagens do TMS × tarifa média por km das viagens com tag):

| Lacuna | Estimada | Valor real (gabarito) | Erro |
|---|---|---|---|
| Extrato de fev/2026 ausente | R$ 61.232,10 | R$ 63.330,21 | -3,3% |
| Pedágio manual sem comprovante | R$ 19.503,39 | R$ 18.466,46 | 5,6% |

## 6. Estimativa progressiva (EMP-A, out/2025 a mar/2026)

Valor real do período (observado + lacunas do gabarito): **R$ 133.176,48**. Faixa = P10 a P90 de 20.000 simulações (não é probabilidade calibrada).

| Nível | Informação disponível | P10 | P50 | P90 | Largura | Parcela observada | Contém o real? |
|---|---|---|---|---|---|---|---|
| N0 | Composição da frota (8 veículos: 4 utilitários e 2 automóveis próprios, 2 automóveis locados), segmento e UF | R$ 119.738 | R$ 137.419 | R$ 157.336 | R$ 37.598 | 0% | sim |
| N1 | + duas respostas: km médio mensal por veículo e gasto mensal com combustível | R$ 126.191 | R$ 135.425 | R$ 145.064 | R$ 18.873 | 0% | sim |
| N2 | + extratos de combustível e pedágio, faturas de locação e 3 meses de notas de oficina (situação atual) | R$ 134.597 | R$ 139.938 | R$ 145.661 | R$ 11.064 | 72% | não |
| N3 | + apólice de seguro, comprovantes de IPVA/licenciamento e relação de multas (simulação do próximo passo) | R$ 130.766 | R$ 133.232 | R$ 136.208 | R$ 5.442 | 89% | sim |

Próximas perguntas no nível N2, ordenadas por redução da faixa por unidade de esforço:

| Ordem | Pergunta | Esforço | Redução da largura | Redução % |
|---|---|---|---|---|
| 1 | Enviar a apólice de seguro (ou informar o prêmio anual) | 1 | R$ 3.827 | 33,9% |
| 2 | Enviar comprovantes de IPVA e licenciamento (ou informar os valores pagos) | 1 | R$ 2.141 | 19,0% |
| 3 | Enviar as notas de oficina de out/2025, nov/2025 e mar/2026 | 2 | R$ 1.362 | 12,1% |
| 4 | Informar se houve multas no período e o valor total pago | 1 | R$ 139 | 1,2% |

Respostas simuladas no N1: km médio declarado 1.810 km/mês (média observada nos veículos com odômetro: 1.679); combustível declarado R$ 8.800/mês.

## 7. Confiabilidade do diagnóstico

| Empresa | C | A | K | R | X | Mínimo | Selo |
|---|---|---|---|---|---|---|---|
| EMP-A | 73,3 | 58,5 | 96,9 | 97,9 | 87,5 | 58,5 | Baixa |
| EMP-B | 100,0 | 100,0 | 100,0 | 99,7 | 100,0 | 99,7 | Alta |
| EMP-C | 99,5 | 100,0 | 99,8 | 99,9 | 100,0 | 99,5 | Alta |

Escala 0-100 por dimensão; o selo usa a pior dimensão (elo mais fraco).

## 8. Oportunidades, cenários e priorização

Economia líquida anual = economia bruta × fator de captura − custo recorrente. Fatores de captura e custos de ação são hipóteses (ver `hipoteses_de_acao` no JSON). Cenários: conservador = só oportunidades validadas; base = + anomalias; otimista = + hipóteses. Os custos recorrentes incluem o custo de operar o plano (EMP-B R$ 12.000/ano; EMP-C R$ 30.000/ano, hipóteses). Recuperações pontuais (contestação de cobranças passadas) não entram na economia anual.

### EMP-B

| Ordem | Id | Oportunidade | Estágio | Bruta anual | Líquida cons. | Líquida base | Líquida otim. | Confiança | Esforço (p-sem) | Prioridade |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OP-B1 | Multas NIC (não indicação do condutor) | oportunidade validada | R$ 2.033 | R$ 1.423 | R$ 1.830 | R$ 2.033 | Alta | 0,50 | 4.575 |
| 2 | OP-B6 | Abastecimento acima da referência de preço da própria frota | oportunidade validada | R$ 2.954 | R$ 886 | R$ 1.477 | R$ 2.068 | Alta | 1,00 | 1.477 |
| 3 | OP-B4 | Custos fixos de 3 utilitários subutilizados | hipotese | R$ 14.083 | não entra | não entra | R$ 9.388 | Baixa | 2,00 | 1.174 |
| 4 | OP-B2 | Multas pagas sem o desconto de 20% | oportunidade validada | R$ 207 | R$ 103 | R$ 165 | R$ 207 | Alta | 0,25 | 661 |
| 5 | OP-B3 | Passagens de pedágio cobradas em duplicidade | oportunidade validada | R$ 315 | R$ 158 | R$ 252 | R$ 315 | Alta | 0,50 | 631 |
| 6 | OP-B5 | Manutenção corretiva elevada em 4 caminhões de 2012-2013 | hipotese | R$ 39.672 | não entra | não entra | R$ 5.436 | Moderada | 3,00 | -129 |

| Cenário | Itens | Bruta capturada | Custos recorrentes | Implantação | Economia líquida anual | Payback (meses) | ROI 12 meses | Recuperação pontual |
|---|---|---|---|---|---|---|---|---|
| conservador | OP-B1, OP-B2, OP-B3, OP-B6 | R$ 2.571 | R$ 12.000 | R$ 2.000 | -R$ 9.429 | n/a | -82% | R$ 315 |
| base | OP-B1, OP-B2, OP-B3, OP-B6 | R$ 3.725 | R$ 12.000 | R$ 2.000 | -R$ 8.275 | n/a | -73% | R$ 315 |
| otimista | OP-B1, OP-B2, OP-B3, OP-B4, OP-B6, OP-B5 | R$ 33.848 | R$ 26.400 | R$ 10.000 | R$ 7.448 | 16,1 | -7% | R$ 315 |

Próximo passo recomendado: **OP-B1 — Multas NIC (não indicação do condutor)**.

### EMP-C

| Ordem | Id | Oportunidade | Estágio | Bruta anual | Líquida cons. | Líquida base | Líquida otim. | Confiança | Esforço (p-sem) | Prioridade |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OP-C1 | Queda de rendimento em 3 cavalos mecânicos | anomalia | R$ 108.080 | não entra | R$ 64.848 | R$ 86.464 | Moderada | 1,50 | 32.424 |
| 2 | OP-C2 | Abastecimento acima da referência de preço da própria frota | oportunidade validada | R$ 135.164 | R$ 35.749 | R$ 62.782 | R$ 89.815 | Alta | 2,00 | 31.391 |
| 3 | OP-C3 | Cobrança de eixo suspenso em retornos vazios | oportunidade validada | R$ 30.663 | R$ 15.331 | R$ 21.464 | R$ 27.596 | Moderada | 1,00 | 20.122 |
| 4 | OP-C4 | Viagens de lotação sem registro de Vale-Pedágio | hipotese | R$ 137.934 | não entra | não entra | R$ 82.760 | Baixa | 2,00 | 10.345 |
| 5 | OP-C5 | Multas NIC (não indicação do condutor) | oportunidade validada | R$ 521 | R$ 364 | R$ 469 | R$ 521 | Alta | 0,50 | 1.171 |
| 6 | OP-C6 | Multas pagas sem o desconto de 20% | oportunidade validada | R$ 39 | R$ 20 | R$ 31 | R$ 39 | Alta | 0,25 | 125 |

| Cenário | Itens | Bruta capturada | Custos recorrentes | Implantação | Economia líquida anual | Payback (meses) | ROI 12 meses | Recuperação pontual |
|---|---|---|---|---|---|---|---|---|
| conservador | OP-C2, OP-C3, OP-C5, OP-C6 | R$ 56.264 | R$ 34.800 | R$ 3.000 | R$ 21.464 | 1,7 | 49% | R$ 30.663 |
| base | OP-C1, OP-C2, OP-C3, OP-C5, OP-C6 | R$ 154.394 | R$ 34.800 | R$ 7.500 | R$ 119.594 | 0,8 | 265% | R$ 30.663 |
| otimista | OP-C1, OP-C2, OP-C3, OP-C4, OP-C5, OP-C6 | R$ 291.995 | R$ 34.800 | R$ 7.500 | R$ 257.195 | 0,3 | 590% | R$ 30.663 |

Próximo passo recomendado: **OP-C1 — Queda de rendimento em 3 cavalos mecânicos**.

### Sensibilidade do cenário-base (EMP-C)

| Variação | Economia líquida anual | Implantação | Custos recorrentes | Payback (meses) | ROI 12 meses |
|---|---|---|---|---|---|
| referencia | R$ 119.594 | R$ 7.500 | R$ 34.800 | 0,8 | 265% |
| captura -20% | R$ 88.715 | R$ 7.500 | R$ 34.800 | 1,0 | 192% |
| custos x2 | R$ 84.794 | R$ 15.000 | R$ 69.600 | 2,1 | 82% |
| captura -20% e custos x2 | R$ 53.915 | R$ 15.000 | R$ 69.600 | 3,3 | 46% |

### Duas alavancas sobre o mesmo custo

Custo de R$ 200.000 com reduções de 6% e 4%: soma ingênua R$ 20.000; efeito combinado R$ 19.520; dupla contagem evitada R$ 480.


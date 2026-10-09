# Solução proposta: Frota Pulse

## 1. Nome e posicionamento

**Frota Pulse — inteligência de custos que transforma dados em decisões** é o nome provisório do projeto acadêmico. Não é marca da Sem Parar Empresas, da Corpay nem da FIAP, e não usa seus logotipos.

Avaliação do nome **[Decisão]**:

| Critério | Avaliação |
|---|---|
| Clareza | "Frota" situa o domínio em português; "Pulse" sugere sinal vital medido com regularidade |
| Coerência com o produto | O valor do produto está no ciclo recorrente (atualizar, medir, agir), que é o centro de US-GF-08 e US-SP-05; "pulso" expressa esse acompanhamento |
| Conflito de nome | Busca na web em outubro de 2026 não encontrou produto de gestão de frota com esse nome no Brasil. Há nomes parecidos em outros contextos: "FleetPulse" (gestão de embarcações) e "Pulse" (software britânico de gestão de veículos, divulgado em 2012). Antes de qualquer uso comercial, seria necessária busca no INPI |
| Alternativas consideradas | "Frota One" é o título do documento de User Stories e pertence ao cliente, então foi descartado para não confundir com produto oficial. "Custo Claro" e "FrotaLens" comunicam diagnóstico, mas não o acompanhamento recorrente. Nenhuma alternativa se mostrou superior |

## 2. Proposta de valor

Para **gestores de frota e líderes financeiros** que pagam combustível, manutenção, pedágio, multas, tributos e seguro em sistemas separados, o Frota Pulse é uma **calculadora de redução de custos** que:

1. aceita os documentos como estão;
2. mostra uma estimativa do custo total desde a primeira resposta, com faixa de incerteza explícita;
3. separa custo alto de ineficiência real;
4. transforma cada achado em ação com economia estimada em R$ por cenário;
5. mede depois a economia realizada.

O diferencial não está em calcular totais, mas em **dizer quanto se pode confiar em cada número e o que fazer para melhorar essa confiança**.

## 3. Cinco capacidades

| Capacidade | O que faz | User Stories | Situação na Sprint 1 | Implementação |
|---|---|---|---|---|
| **C1 Understand** (entender) | Recebe documentos em vários formatos, extrai, classifica, padroniza, valida e preserva a origem de cada valor | GF-01, GF-09, GF-10, SP-04, SP-06 | Especificada; regras de qualidade demonstradas na massa sintética | S2 (estruturados), S3 (PDF, imagem, texto) |
| **C2 Diagnose** (diagnosticar) | Consolida custos, calcula indicadores normalizados, detecta desvios e classifica a evidência | GF-02, GF-03, CF-03, CF-04 | Especificada; indicadores, CUSUM e decomposição demonstrados | S2 e S3 |
| **C3 Compare** (comparar) | Compara com histórico próprio, pares, grupos entre clientes e referências externas, só quando há equivalência | GF-04, SP-03 | Especificada; pares e histórico demonstrados | S3; grupos entre clientes após piloto |
| **C4 Optimize** (otimizar) | Recomenda ações, estima economia por cenário, prioriza e define o próximo passo | GF-05, GF-06, GF-07, CF-01, CF-02, SP-01, SP-02 | Especificada; cenários, sensibilidade e priorização demonstrados | S3 e S4 |
| **C5 Monitor** (acompanhar) | Atualizações periódicas, comparação entre períodos, economia realizada e recalibração das premissas | GF-08, SP-05 | Especificada; mecânica de calibração demonstrada | S4 em diante |

"Demonstrado" significa que o método foi executado sobre dados sintéticos por um script reproduzível ([anexo de exemplos](anexos/exemplos-calculados.md)). Não significa que exista aplicação.

## 4. Princípios do briefing e como o produto os cumpre

| Princípio [Briefing] | Texto original | Decisões de produto |
|---|---|---|
| **Simples** | "Sem treinamento, sem manual." | Fluxo guiado por perguntas; uma ação destacada como próximo passo; vocabulário de gestão, não estatístico ("faixa provável", não "P10-P90") |
| **Confiável** | "Números com premissa clara." | Todo valor tem status (observado, corrigido, imputado, estimado ou não disponível), origem e premissa; índice de confiabilidade com 5 dimensões; cálculos financeiros determinísticos e versionados |
| **Flexível** | "Qualquer formato de input." | Ingestão de CSV, XLSX, PDF, imagem, print, texto e extratos; revisão humana quando a confiança da extração é baixa |
| **Progressivo** | "Útil desde o primeiro dado." | Estimativa com faixa já no nível N0 (só a composição da frota); cada informação estreita a faixa; perguntas ordenadas pelo ganho de precisão |

## 5. Funcionalidades

| ID | Funcionalidade | Capacidade | User Stories | MoSCoW | Sprint |
|---|---|---|---|---|---|
| F01 | Ingestão multiformato com fila de revisão humana | C1 | GF-01 | Must | S2, S3 |
| F02 | Perguntas guiadas e próxima melhor pergunta | C1 | GF-10, SP-04 | Must | S2 |
| F03 | Estimativa progressiva com faixa e parcela observada | C1, C2 | GF-09, SP-04 | Must | S2, S3 |
| F04 | Painel consolidado (custo total, por categoria, por veículo, caixa e competência) | C2 | GF-02, CF-03 | Must | S2 |
| F05 | Trilha de cálculo de cada indicador (dado → fórmula → resultado) | C2 | GF-02, CF-03 | Must | S2 |
| F06 | Detecção de desvios e mapa de ineficiências por estágio de evidência | C2 | GF-03, CF-04 | Must | S3 |
| F07 | Benchmark hierárquico com regras de comparabilidade | C3 | GF-04, SP-03 | Must | S3 |
| F08 | Catálogo de recomendações com associação condicionada ao portfólio | C4 | GF-05, SP-01 | Must | S3 |
| F09 | Economia em R$ por cenário, com payback, ROI e sensibilidade | C4 | GF-06, CF-02 | Must | S3 |
| F10 | Priorização e próximo passo | C4 | GF-07, CF-04 | Must | S3 |
| F11 | Relatório executivo exportável (uma página) | C4 | CF-01 | Must | S4 |
| F12 | Atualização periódica e comparação entre períodos | C5 | GF-08, SP-05 | Should | S4 |
| F13 | Medição de economia realizada (linha de base ajustada) | C5 | GF-08, CF-02 | Should | S4 |
| F14 | Índice de confiabilidade do diagnóstico | C2 | GF-09 | Must | S2 |
| F15 | Preferências de contato e base legal por finalidade | C1, C4 | SP-02, SP-06 | Should | S2, S4 |
| F16 | Painel interno da Sem Parar Empresas (agregado, autorizado e auditado) | C3, C4 | SP-02, SP-03 | Could | S4 |
| F17 | Lembretes com novidade calculada | C5 | GF-08, SP-05 | Should | S4 |

## 6. Diferenciais avaliados

Cada diferencial foi avaliado por três perguntas: atende a alguma User Story? É verificável? O custo de construir cabe no prazo?

| Diferencial | Decisão | Justificativa |
|---|---|---|
| Diagnóstico progressivo | **Adotado (núcleo)** | Exigido por US-GF-09 e pelo princípio "Progressivo" |
| Índice de completude | **Adotado** como dimensão C do índice de confiabilidade | Isolado, esconderia problemas de atualidade ou consistência |
| Indicador de confiabilidade | **Adotado**: 5 dimensões, selo pela pior | Torna "Confiável" verificável; o selo pelo pior evita que uma média esconda uma falha crítica |
| Benchmark contextualizado | **Adotado com restrição** | Histórico próprio e pares desde o início; grupos entre clientes dependem de autorização e volume mínimo |
| Simulação de cenários | **Adotado** em escada de evidência | O CFO precisa separar o validado do hipotético (US-CF-02) |
| Priorização por impacto e viabilidade | **Adotado** | US-GF-07 e US-CF-04 |
| Rastreabilidade dado → cálculo → recomendação | **Adotado** | Sem ela, "número com premissa clara" não é auditável |
| Decomposição atividade × intensidade × preço | **Adotado** (proposta do grupo) | Impede tratar volume como desperdício e evita dupla contagem entre preço e consumo |
| Estimativa de lacunas por dados de contexto | **Adotado** (proposta do grupo) | Viagens sem pedágio registrado indicam lacuna e permitem estimá-la; no exemplo, o erro foi de -3,3% e +5,6% |
| Orientações para melhorar os dados | **Adotado** como perguntas guiadas por ganho de precisão | US-GF-10 |
| Visões para gestor e para CFO | **Adotado** | Personas com perguntas diferentes |
| Relação com soluções Sem Parar Empresas | **Adotado com regra de associação** | US-SP-01, sem associação automática e sem promessa de economia |
| Assistente conversacional (LLM) | **Adiado** (S4 ou depois) | Útil para explicar, arriscado para calcular; só entra com verificação numérica ([estratégia de IA](estrategia-ia.md)) |
| Integrações por API (tags, cartões, telemetria) | **Adiado** | Dependem de acordos e documentação técnica ainda não disponíveis |
| Manutenção preditiva por aprendizado de máquina | **Descartado nesta fase** | Exige histórico por componente que os clientes não têm no início; métodos estatísticos simples atendem às User Stories |
| Pontuação individual de motoristas | **Descartado nesta fase** | Não é pedida nas User Stories e aumenta riscos de privacidade e de uso disciplinar |

## 7. Como o produto funciona

**Primeiro acesso (C1).** O gestor informa quantos veículos tem, de que tipo e em que operação. O produto devolve uma faixa de custo total e a pergunta que mais estreita essa faixa. No exemplo sintético da EMP-A, a faixa inicial vai de R$ 116.158 a R$ 155.401 em seis meses.

**Primeiros documentos (C1, C2).** O gestor envia extratos e notas como estão. O produto extrai, valida, separa o que precisa de revisão e mostra o custo consolidado com a parcela observada e o selo de confiança.

**Diagnóstico (C2, C3).** Indicadores normalizados, comparação com histórico e pares, e achados classificados em observação, anomalia, hipótese ou oportunidade validada.

**Plano de ação (C4).** Cada achado vira ação com responsável, economia em R$ por cenário e prioridade. Um próximo passo fica em destaque. Quando a regra de associação é satisfeita, a recomendação cita a solução da Sem Parar Empresas relacionada.

**Ciclo mensal (C5).** Novos dados atualizam os indicadores; ações concluídas passam a ter economia realizada medida; as premissas são recalibradas.

As jornadas e os wireframes estão em [UX e identidade visual](ux-identidade-visual.md).

## 8. O que o produto não promete

- **Economia garantida.** Todo valor futuro é estimativa com premissas visíveis. Economia realizada só existe depois de medida contra linha de base ajustada.
- **Parecer jurídico.** Achados com base legal, como multa NIC, eixo suspenso e Vale-Pedágio, indicam onde verificar, não substituem análise jurídica.
- **Associação automática a produtos.** Contratar uma solução não garante economia específica, e o produto não afirma isso.
- **Precisão sem dados.** Com pouca informação, a faixa é larga, e o produto diz isso em vez de esconder.

# User Stories e rastreabilidade

## 1. Fonte e convenções

As 20 User Stories abaixo são as **oficiais**, transcritas sem alteração do documento "User Stories — Calculadora de Frota One" (briefing, p. 3-4, rodapé "Documento executivo • 20 user stories • 2026"). O documento original não numera as histórias; os identificadores foram atribuídos pelo grupo na ordem em que aparecem:

- **US-GF-01 a US-GF-10**: visão gestor de frota
- **US-CF-01 a US-CF-04**: visão CFO e liderança
- **US-SP-01 a US-SP-06**: visão Sem Parar Empresas

Duas histórias não trazem a cláusula "para [benefício]" no original (US-GF-10 e US-SP-06). Nelas, o benefício abaixo está marcado como **[inferido]**.

**Priorização.** O método é MoSCoW (*Must, Should, Could, Won't this time*), técnica associada a Dai Clegg e ao DSDM ([referências](referencias.md)). A classificação considera valor para as personas, dependências técnicas e risco, dentro do horizonte de 8 meses do briefing. **Complexidade:** P (até 1 semana-pessoa), M (1 a 3), G (mais de 3). **Sprint prevista:** S2 a S4, conforme o [roadmap](roadmap.md); a quantidade de Sprints é hipótese de planejamento até a confirmação do calendário oficial.

As funcionalidades F01 a F17 e as capacidades C1 a C5 estão definidas em [solução](solucao.md).

## 2. Matriz-resumo

| ID | Persona | Funcionalidades | MoSCoW | Complex. | Sprint | Depende de | Evidência na Sprint 1 |
|---|---|---|---|---|---|---|---|
| US-GF-01 | G | F01 | Must | G | S2 (CSV/XLSX), S3 (PDF, imagem, texto) | — | [Ingestão](ingestao-qualidade.md), regras R-* testadas no [anexo](anexos/exemplos-calculados.md#1-regras-de-qualidade-aplicadas-aos-cenários-injetados) |
| US-GF-02 | G | F04, F05 | Must | M | S2 | GF-01 | [IND-01 a IND-04](diagnostico.md#3-indicadores), caixa × competência no anexo |
| US-GF-03 | G | F06 | Must | G | S3 | GF-02 | [Taxonomia de evidência](diagnostico.md#2-da-observação-à-economia-realizada), CUSUM e LMDI no anexo |
| US-GF-04 | G | F07 | Must | G | S3 (própria frota), S4+ (entre clientes) | GF-02 | [Benchmarks](benchmarks.md) |
| US-GF-05 | G | F08 | Must | M | S3 | GF-03 | [Catálogo REC-01 a REC-14](economia-recomendacoes.md#6-catálogo-de-recomendações) |
| US-GF-06 | G | F09 | Must | M | S3 | GF-05 | [Metodologia de economia](economia-recomendacoes.md#2-convenção-de-sinais-e-fórmulas) |
| US-GF-07 | G | F10 | Must | P | S3 | GF-06 | [Priorização e próximo passo](economia-recomendacoes.md#5-priorização-e-próximo-passo) |
| US-GF-08 | G | F12, F13, F17 | Should | M | S4 | GF-01, GF-02 | [Capacidade Monitor](solucao.md#3-cinco-capacidades) e medição de economia realizada |
| US-GF-09 | G | F03, F14 | Must | G | S2 (N0 a N2), S3 (calibração) | GF-10 | [Estimativa progressiva](diagnostico.md#5-estimativa-progressiva-e-perguntas-guiadas) |
| US-GF-10 | G | F02 | Must | M | S2 | — | Próximas perguntas por valor da informação, no anexo |
| US-CF-01 | F | F11 | Must | M | S4 | GF-06, GF-07 | [Wireframe do relatório](ux-identidade-visual.md#5-wireframes-conceituais) |
| US-CF-02 | F | F09 | Must | P | S3 | GF-06 | Cenários, payback, ROI e sensibilidade no anexo |
| US-CF-03 | L | F04, F05 | Must | M | S2 | GF-02 | IND-01 a IND-05 com definição fixa |
| US-CF-04 | L | F06, F10 | Must | P | S3 | GF-03, GF-06 | Priorização no anexo |
| US-SP-01 | S | F08 | Should | M | S3 (catálogo), S4 (validação SPE) | GF-05 | [Relação com o portfólio](economia-recomendacoes.md#7-relação-com-o-portfólio-sem-parar-empresas) |
| US-SP-02 | S | F15, F16 | Could | M | S4 | GF-06, SP-06 | [Finalidades comerciais e LGPD](seguranca-lgpd.md#4-finalidades-comerciais-leads-e-benchmarks) |
| US-SP-03 | S | F07, F16 | Could | G | S4 (mecânica), após piloto (produção) | GF-04, SP-06 | [Grupos entre clientes](benchmarks.md#2-hierarquia-de-referências), backtest de calibração |
| US-SP-04 | S | F02, F03 | Must | M | S2 a S4 (medida em S4) | GF-09, GF-10 | Faixa N0 a N3 e perguntas no anexo |
| US-SP-05 | S | F12, F17 | Should | M | S4 | GF-08 | Capacidade Monitor |
| US-SP-06 | S | F15 | Should, com restrições legais | M | S2 (cadastro), S4 (preferências) | — | [Consentimento e base legal](seguranca-lgpd.md#4-finalidades-comerciais-leads-e-benchmarks) |

Nenhuma User Story oficial foi classificada como *Won't*. O que o projeto não fará é a **interpretação irrestrita** de US-SP-06 ("sempre ter as informações [...] para tratá-los como leads"): o contato de serviço é sempre registrado, mas o uso comercial depende de base legal e da preferência do titular (ver US-SP-06 abaixo).

## 3. Detalhamento por User Story

### Visão gestor de frota

#### US-GF-01
> "Como gestor de frota, quero inserir os dados da minha frota em diferentes formatos (imagens, pdfs, prints, excel...), para não precisar estruturar ou tratar os dados antes de utilizar a calculadora."

- **Necessidade:** usar os documentos como estão. **Benefício:** menos trabalho manual antes de ter resultado.
- **Funcionalidade:** F01, ingestão multiformato (CSV, XLSX, PDF com texto, PDF escaneado, imagem, print, texto livre, extratos) com extração, classificação, padronização, validação e fila de revisão humana.
- **Dados:** arquivos do cliente; hash, tipo, método e confiança de extração ([`origens_dados`](modelagem-dados.md#3-dicionário-de-dados)).
- **Critério de aceitação:** (1) CSV e XLSX de extratos importados com 100% das linhas válidas, cada registro com origem, localizador e hash; (2) PDF e imagem geram registros com confiança por campo, e os abaixo de 0,80 vão para revisão; (3) reenvio do mesmo arquivo é detectado (R-DUP-ARQ) e não altera totais; (4) nenhum valor é preenchido sem marcação de status.
- **Como verificar:** testes automatizados com a massa sintética (os cenários G01, G10, G11 e G28 já têm gabarito) e amostra rotulada de documentos (Sprint 3).

#### US-GF-02
> "Como gestor de frota, quero visualizar o custo total da minha frota de forma consolidada, para entender quanto realmente estou gastando com a operação."

- **Necessidade:** um número confiável de custo total. **Benefício:** saber o gasto real.
- **Funcionalidade:** F04 (painel consolidado por categoria, veículo e mês) e F05 (trilha de cálculo de cada indicador).
- **Dados:** despesas válidas com competência; cadastro de veículos.
- **Critério de aceitação:** custo total igual à soma dos registros válidos (teste de igualdade); visões por caixa e por competência, com custos plurimensais rateados; duplicidades excluídas e registros em quarentena exibidos à parte.
- **Como verificar:** no anexo, a EMP-B mostra a diferença entre caixa e competência em abr/2026 (renovação do seguro).

#### US-GF-03
> "Como gestor de frota, quero identificar onde estão as principais ineficiências da minha operação, para saber quais custos devo atacar primeiro."

- **Necessidade:** separar custo alto de desperdício. **Benefício:** atacar primeiro o que importa.
- **Funcionalidade:** F06, detecção de desvios (regras, escore z robusto, CUSUM) e decomposição do custo em atividade, intensidade e preço.
- **Dados:** custos por veículo e mês, km, litros, preço, categoria e modalidade.
- **Critério de aceitação:** cada achado traz estágio de evidência, indicador, método, registros de origem e confiança; nos cenários G12, G13 e G24, os veículos e viagens injetados aparecem entre os achados, e nos cenários G26 e G08 (custo alto justificável) não aparecem como ineficiência.
- **Como verificar:** comparação automática com o gabarito sintético; validação qualitativa com gestores (Sprint 4).

#### US-GF-04
> "Como gestor de frota, quero comparar meus custos com um benchmark, para entender se minha operação está eficiente em relação a outras referências."

- **Necessidade:** referência justa. **Benefício:** saber se a operação é eficiente.
- **Funcionalidade:** F07, benchmark hierárquico: histórico próprio, pares da frota, grupos entre clientes, referências externas e cenários hipotéticos, com regras BEN-01 a BEN-08.
- **Dados:** indicadores normalizados; categoria, modalidade, UF, período; para grupos entre clientes, autorização de uso agregado.
- **Critério de aceitação:** toda comparação mostra tipo de referência, número de veículos ou empresas e período; sem equivalência, o produto explica por que não compara.
- **Como verificar:** testes das regras BEN com casos de borda (grupo pequeno, veículos locados, período desalinhado).

#### US-GF-05
> "Como gestor de frota, quero receber recomendações de ações para cada nível de ineficiência, para transformar o diagnóstico em ações concretas."

- **Necessidade:** saber o que fazer. **Benefício:** transformar diagnóstico em ação.
- **Funcionalidade:** F08, catálogo de recomendações (REC-01 a REC-14) por estágio de evidência: para hipóteses, a ação é investigar; para oportunidades validadas, executar.
- **Dados:** achados, catálogo, responsáveis.
- **Critério de aceitação:** todo achado em estágio de anomalia ou superior tem ao menos uma ação, com responsável sugerido, métrica de acompanhamento e prazo de revisão.

#### US-GF-06
> "Como gestor de frota, quero visualizar a economia potencial em R$, para conseguir priorizar as ações de maior impacto financeiro."

- **Necessidade:** valor em reais. **Benefício:** priorizar por impacto.
- **Funcionalidade:** F09, economia bruta, fator de captura, economia líquida, cenários e tratamento de sobreposição.
- **Dados:** custo elegível, referência ajustada, hipóteses de captura e de custo de ação.
- **Critério de aceitação:** fórmula e premissas visíveis em cada valor; teste de dupla contagem aprovado; hipóteses separadas de oportunidades validadas.

#### US-GF-07
> "Como gestor de frota, quero saber qual é o próximo passo recomendado após o diagnóstico, para não ficar apenas com uma análise dos problemas."

- **Funcionalidade:** F10, priorização por valor, confiança, urgência e esforço, com destaque do próximo passo.
- **Critério de aceitação:** um único próximo passo destacado, com motivo, responsável e data de revisão. No exemplo da EMP-C, o próximo passo calculado é a inspeção dos três cavalos mecânicos com queda de rendimento (OP-C1).

#### US-GF-08
> "Como gestor de frota, quero atualizar meus dados periodicamente, para acompanhar a evolução dos custos e identificar novas oportunidades de economia."

- **Funcionalidade:** F12 (atualização incremental e comparação entre períodos), F13 (economia realizada) e F17 (lembretes).
- **Critério de aceitação:** novo envio mensal atualiza indicadores e versões; reenvio duplicado não altera totais; ações concluídas passam a ter economia realizada medida contra linha de base ajustada.

#### US-GF-09
> "Como gestor de frota, quero sempre ter algum tipo de estimativa do meu custo total, menos preciso se eu der menos informações e mais preciso se eu der informações mais completas."

- **Funcionalidade:** F03 (estimativa progressiva com faixa P10-P90) e F14 (índice de confiabilidade).
- **Dados:** composição da frota (mínimo), respostas guiadas, documentos.
- **Critério de aceitação:** com apenas a composição da frota, retorna faixa e valor central; a largura da faixa diminui a cada nível de informação; a parcela observada do custo é exibida. No anexo, a largura cai de R$ 39.243 (N0) para R$ 8.416 (N3).
- **Limitação registrada:** faixa estreita não garante acerto. No N3 do exemplo, o valor real ficou acima do P90, e por isso a calibração por backtest é critério de aceite da Sprint 3.

#### US-GF-10
> "Como gestor de frota, quero que me façam perguntas e indiquem qual tipo de informação devo fornecer."

- **Benefício [inferido]:** fornecer só o que melhora o resultado, com menos esforço.
- **Funcionalidade:** F02, perguntas guiadas ordenadas pela redução esperada da faixa por unidade de esforço.
- **Critério de aceitação:** a cada estado, o produto mostra as próximas perguntas com o ganho esperado em R$; no exemplo da EMP-A, a primeira pergunta é a apólice de seguro.

### Visão CFO e liderança

#### US-CF-01
> "Como CFO, quero receber um relatório executivo com os principais custos e oportunidades da frota, para tomar decisões de forma rápida e objetiva."

- **Funcionalidade:** F11, relatório de uma página (PDF) com custo total, R$/km, três principais oportunidades, cenários, selo de confiança e premissas.
- **Critério de aceitação:** relatório gerado a partir do mesmo diagnóstico do painel (sem recálculo divergente), com data, versão da metodologia e selo; validado com ao menos 2 responsáveis financeiros na Sprint 4.

#### US-CF-02
> "Como CFO, quero visualizar a economia potencial em R$, para entender o impacto financeiro das oportunidades identificadas."

- **Funcionalidade:** F09 na visão executiva: economia líquida por cenário, payback, ROI, sensibilidade e separação entre economia recorrente e recuperação pontual.
- **Critério de aceitação:** nenhum valor sem premissa; hipóteses só no cenário otimista.

#### US-CF-03
> "Como líder da operação, quero ter uma visão consolidada dos custos da frota, para acompanhar a eficiência da operação sem depender de análises manuais."

- **Funcionalidade:** F04 e F05 com indicadores de definição estável (IND-01 a IND-05) e versionamento da metodologia.
- **Critério de aceitação:** mesmos indicadores todo mês; mudança de definição gera nova versão e nota explicativa.

#### US-CF-04
> "Como líder, quero identificar as principais oportunidades de redução de custos, para direcionar investimentos e esforços para as iniciativas de maior impacto."

- **Funcionalidade:** F06 e F10, lista priorizada com estágio de evidência e esforço.
- **Critério de aceitação:** ordenação reprodutível pela fórmula de prioridade, com os fatores visíveis.

### Visão Sem Parar Empresas

#### US-SP-01
> "Como Sem Parar Empresas, quero transformar o diagnóstico de custos em recomendações conectadas às nossas soluções, para ajudar o cliente a reduzir seus custos de frota."

- **Funcionalidade:** F08 com regra de associação: a solução aparece só quando a causa do achado está no escopo dela e a evidência atinge o mínimo definido; o texto nunca promete economia específica do produto.
- **Critério de aceitação:** cada associação registra a regra satisfeita; o catálogo é revisado com a Sem Parar Empresas antes do piloto **[Pendência]**.

#### US-SP-02
> "Como Sem Parar Empresas, quero identificar clientes com oportunidades relevantes de redução de custos, para gerar leads qualificados para o comercial."

- **Funcionalidade:** F15 e F16, painel interno de oportunidades agregadas, restrito a clientes com autorização registrada ou base legal documentada, com trilha de auditoria.
- **Critério de aceitação:** cliente sem autorização não aparece; acesso de cada analista registrado; motivo e valor estimado visíveis.

#### US-SP-03
> "Como Sem Parar Empresas, quero utilizar os dados dos diagnósticos para melhorar continuamente nossos benchmarks, para tornar a calculadora mais precisa conforme sua utilização aumenta."

- **Funcionalidade:** F07 e F16, grupos de referência entre clientes com no mínimo 10 empresas e regra de dominância, e recalibração periódica das premissas.
- **Critério de aceitação:** recalibração versionada; ganho medido por backtest (cobertura e erro da faixa). O anexo já demonstra a mecânica: o erro mediano da faixa de manutenção cai de 24,1% para 8,8% após calibração com histórico.

#### US-SP-04
> "Como Sem Parar Empresas, quero que o cliente perceba valor já no primeiro uso, para aumentar a recorrência de utilização da calculadora."

- **Funcionalidade:** F02 e F03: estimativa no primeiro acesso, com poucas perguntas, e um achado acionável assim que houver um extrato.
- **Critério de aceitação:** primeira estimativa em até 5 minutos e com até 5 perguntas (meta a validar em teste de usabilidade).

#### US-SP-05
> "Como Sem Parar Empresas, quero que o gestor retorne periodicamente para atualizar seus dados, para criar uma relação recorrente com a ferramenta e gerar novas oportunidades comerciais."

- **Funcionalidade:** F12 e F17, lembretes com novidade calculada (variação, novo achado ou economia realizada), enviados só a quem optou por recebê-los.
- **Critério de aceitação:** lembrete sempre com conteúdo novo; descadastro em um clique.

#### US-SP-06
> "Como Sem Parar Empresas, quero sempre ter as informações do cliente para poder entrar em contato e tratá-los como leads."

- **Benefício [inferido]:** continuidade do relacionamento comercial.
- **Funcionalidade:** F15, cadastro com contato de serviço do representante e preferências por finalidade (contato comercial, uso agregado em benchmark), com histórico e revogação.
- **Critério de aceitação:** preferências registradas com versão do termo e data; painel comercial respeita a preferência; revogação efetiva em até 24 horas (meta).
- **Atendimento parcial, por decisão:** "sempre" não pode significar contato comercial sem base legal. Os dados de contato de uma pessoa (o representante) são dados pessoais; o uso comercial exige base legal adequada, como consentimento ou legítimo interesse com teste de balanceamento, além de transparência e possibilidade de oposição ([segurança e LGPD](seguranca-lgpd.md#4-finalidades-comerciais-leads-e-benchmarks)).

## 4. Cobertura por capacidade

| Capacidade | User Stories |
|---|---|
| C1 Understand (entender os dados) | GF-01, GF-09, GF-10, SP-04, SP-06 |
| C2 Diagnose (diagnosticar) | GF-02, GF-03, CF-03, CF-04 |
| C3 Compare (comparar) | GF-04, SP-03 |
| C4 Optimize (otimizar) | GF-05, GF-06, GF-07, CF-01, CF-02, SP-01, SP-02 |
| C5 Monitor (acompanhar) | GF-08, SP-05 |

Todas as 20 User Stories têm funcionalidade, critério de aceitação, Sprint prevista e evidência documental nesta Sprint.

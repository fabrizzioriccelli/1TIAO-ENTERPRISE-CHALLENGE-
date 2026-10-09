# Personas e necessidades

> As personas abaixo são **hipotéticas**. Foram derivadas das 20 User Stories e do documento executivo do briefing; não vêm de entrevistas ou pesquisa de campo, que ainda não foram feitas. A validação com gestores reais está prevista no [roadmap](roadmap.md) (Sprint 4) e o roteiro de entrevista está no fim deste documento.

## Visão geral

| Persona | Quem representa | User Stories de origem | Pergunta que precisa responder |
|---|---|---|---|
| **G — Gestão de frota** | Responsável operacional pela frota, em empresa pequena, média ou grande | US-GF-01 a US-GF-10 | "Onde estou perdendo dinheiro e o que faço primeiro?" |
| **F — Finanças (CFO)** | Diretor ou gerente financeiro que aprova orçamento e investimentos | US-CF-01, US-CF-02 | "Quanto custa a frota, quanto dá para economizar e com que segurança?" |
| **L — Liderança de operação** | Diretor de operações ou logística | US-CF-03, US-CF-04 | "A operação está eficiente sem que eu precise montar planilhas?" |
| **S — Sem Parar Empresas** | Times de produto, comercial e dados da Sem Parar Empresas | US-SP-01 a US-SP-06 | "Como gerar valor para o cliente, recorrência e oportunidades comerciais legítimas?" |

Os identificadores das User Stories estão em [User Stories](user-stories.md).

## G — Gestão de frota

**Contexto hipotético.** Coordena entre 8 e 80 veículos, acumula outras funções (compras, manutenção, escalas) e trabalha com planilhas e extratos de fornecedores diferentes: extrato da tag de pedágio, fatura do cartão de combustível, notas de oficina, notificações de multa e boletos de IPVA. O perfil varia muito com o porte e o segmento, e por isso o produto trata as três frotas sintéticas como casos distintos ([modelagem de dados](modelagem-dados.md#5-massa-de-dados-sintéticos)).

| Aspecto | Descrição |
|---|---|
| Objetivos | Consolidar despesas; enxergar custo por veículo e categoria; achar desperdícios; priorizar intervenções; reduzir trabalho manual; acompanhar a operação mês a mês |
| Dores | Dados espalhados; pouco tempo para organizar planilhas; dificuldade de explicar à diretoria por que o custo subiu; não saber se um valor alto é problema ou consequência de rodar mais |
| Decisões que toma | Quais veículos inspecionar; onde e como abastecer; como tratar multas e prazos; quando renovar ou desmobilizar um veículo; quais cobranças contestar |
| Informação de que precisa | Custo total e por categoria; R$/km por veículo; desvios em relação ao histórico e aos pares; lista curta de ações com R$ estimado; o que falta enviar para melhorar o diagnóstico |
| Sinais de sucesso | Primeira estimativa em poucos minutos; menos horas consolidando dados; ações com resultado medido; menos multas NIC e cobranças indevidas |
| Risco de má interpretação | Tratar uma estimativa como fato. O produto sempre mostra faixa, parcela observada e selo de confiança |

## F — Finanças (CFO)

**Contexto hipotético.** Recebe a frota como linha de despesa relevante, com picos de caixa (seguro anual, IPVA) que não explicam a eficiência. Decide orçamento, renovação de ativos e iniciativas de redução de custo.

| Aspecto | Descrição |
|---|---|
| Objetivos | Conhecer o custo total da operação (TCO) e sua tendência; comparar iniciativas pelo retorno; entender riscos e incertezas |
| Dores | Números sem premissa clara; economia prometida que não aparece; relatórios operacionais longos demais |
| Decisões que toma | Aprovar ou não um plano de ação; alocar investimento; definir metas de custo |
| Informação de que precisa | Custo por competência e por caixa; economia líquida por cenário (conservador, base, otimista); payback e ROI; premissas e confiança de cada número; separação entre economia recorrente e recuperação pontual |
| Sinais de sucesso | Relatório de uma página lido em poucos minutos; decisões tomadas com base em cenários; economia realizada medida depois |
| Risco de má interpretação | Somar oportunidades sobrepostas ou hipóteses não validadas. O relatório separa estágios de evidência e evita dupla contagem ([economia](economia-recomendacoes.md#4-dupla-contagem)) |

## L — Liderança de operação

**Contexto hipotético.** Acompanha a eficiência da operação e o nível de serviço. Precisa de visão consolidada sem depender de análises manuais.

| Aspecto | Descrição |
|---|---|
| Objetivos | Acompanhar a eficiência ao longo do tempo; saber onde concentrar esforço e investimento |
| Dores | Indicadores que mudam de definição a cada relatório; comparações entre operações diferentes |
| Decisões que toma | Prioridades da operação; dimensionamento da frota; metas por unidade |
| Informação de que precisa | Indicadores normalizados (R$/km, R$/veículo·mês, km/L), tendência, desvios relevantes e as principais oportunidades em R$ |
| Sinais de sucesso | Mesmos indicadores todo mês, com definição estável; menos reuniões para conciliar números |
| Risco de má interpretação | Comparar frotas de modalidades diferentes. As regras de comparabilidade bloqueiam comparações sem equivalência ([benchmarks](benchmarks.md#3-quando-não-comparar)) |

## S — Sem Parar Empresas

**Contexto hipotético.** Três papéis internos com interesses diferentes: produto (engajamento e recorrência), comercial (oportunidades qualificadas) e dados (benchmarks melhores com escala).

| Aspecto | Descrição |
|---|---|
| Objetivos | Valor percebido no primeiro uso; retorno periódico do gestor; recomendações conectadas ao portfólio quando fizer sentido; leads qualificados; benchmarks mais precisos com o uso |
| Dores | Leads frios; ferramentas de diagnóstico abandonadas após o primeiro acesso; dados de clientes que não podem ser usados sem base legal |
| Decisões que toma | Quem abordar e com qual oferta; como evoluir benchmarks e catálogo de recomendações |
| Informação de que precisa | Oportunidades agregadas por tipo e porte, só de clientes que autorizaram contato; indicadores de adoção; qualidade e cobertura dos benchmarks |
| Sinais de sucesso | Conversão de oportunidades com autorização registrada; taxa de retorno mensal; redução da largura das faixas de estimativa conforme a base cresce |
| Risco de má interpretação | Associar automaticamente toda ineficiência a um produto, ou usar dados do diagnóstico para fins comerciais sem base legal. O projeto trata os dois casos em [economia e recomendações](economia-recomendacoes.md#7-relação-com-o-portfólio-sem-parar-empresas) e [segurança e LGPD](seguranca-lgpd.md#4-finalidades-comerciais-leads-e-benchmarks) |

## Tensões entre personas

| Tensão | Lado A | Lado B | Como o produto equilibra |
|---|---|---|---|
| Simplicidade × completude | Gestor quer usar sem preparar dados | Diagnóstico confiável exige dados completos | Estimativa progressiva: útil desde o primeiro dado, mais precisa a cada envio |
| Valor ao cliente × interesse comercial | Cliente quer economia, não oferta | SPE quer oportunidades comerciais | Recomendação neutra primeiro; solução SPE aparece só quando a regra de associação é satisfeita, sempre identificada como tal |
| Lead sempre disponível × direitos do titular | SPE quer "sempre ter as informações do cliente" (US-SP-06) | Representante do cliente pode recusar contato comercial | Contato de serviço é sempre registrado; contato comercial depende de autorização ou de avaliação de legítimo interesse, com opção de recusa |
| Relatório rápido × rigor | CFO quer uma página | Números precisam de premissa | Relatório curto com selo de confiança e link para a trilha de cálculo |

## Roteiro de entrevista para validar as personas (Sprint 4)

Perguntas abertas para 5 a 8 gestores de frota e 2 a 3 responsáveis financeiros, com consentimento registrado e sem gravar dados de clientes:

1. Como você descobre hoje quanto a frota custou no mês? Quanto tempo isso leva?
2. Quais documentos você já tem em formato digital? Quais chegam em papel ou foto?
3. Conte a última vez que um custo subiu sem explicação. O que você fez?
4. Que informação faria você confiar em uma estimativa de economia?
5. Com que frequência você atualizaria os dados se a ferramenta mostrasse algo novo a cada mês?
6. Em que situação você aceitaria ser contatado por um fornecedor a partir do diagnóstico?

Critério para revisar uma persona: um padrão citado por pelo menos 3 entrevistados que contradiga a descrição atual.

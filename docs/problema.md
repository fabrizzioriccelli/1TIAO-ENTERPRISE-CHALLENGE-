# Problema, contexto e objetivos

> Documento da Sprint 1. Cada afirmação indica a origem: **[Briefing]** é o material oficial do desafio (PDF de 4 páginas da Sem Parar Empresas), **[Template]** é o repositório modelo da FIAP, **[Enunciado]** é o texto oficial da atividade no portal, **[Decisão]** é escolha do grupo e **[Pendência]** depende de informação externa.

## 1. Contexto

A Sem Parar Empresas faz parte da Corpay, que se apresenta como uma das maiores empresas de pagamentos corporativos do mundo, presente em mais de 100 países. No Brasil, a Sem Parar é descrita como uma das principais operações do grupo, com soluções de mobilidade e benefícios **[Briefing, p. 1]**.

O briefing traz os seguintes números da Sem Parar Empresas, sem data de referência nem metodologia **[Briefing, p. 1]**:

| Indicador do briefing | Valor informado |
|---|---|
| CNPJs | 243 mil |
| Tags | 1,4 milhão |
| Pedágio (*toll*) | R$ 5,88 bilhões |
| Clientes de combustível (*fuel*) | 7,3 mil |

Esses números servem apenas para dimensionar a base potencial de clientes. O projeto não os usa em cálculos e não presume acesso a dados da empresa.

O portfólio citado no briefing organiza-se assim:

| Frente | Soluções citadas |
|---|---|
| Mobilidade (embarcadores, transportadores e frotas leves) | Tag Sem Parar, Vale-Pedágio, Multiabastece, Gestor de Multas |
| Novos negócios em mobilidade | Gestão de Manutenção, Antecipação de Recebíveis, Seguros |
| Benefícios (RH, financeiro e donos de empresa) | Transporte, VR+VA, Multi |

## 2. O problema

O briefing resume o problema em três frases **[Briefing, p. 2]**:

> "O gestor sabe quanto gastou — mas não onde está perdendo. Combustível, manutenção, pedágio, multas e impostos vivem em sistemas separados. A gestão é reativa e o custo real nunca aparece consolidado."

A análise do grupo **[Decisão]** decompõe essa frase em cinco problemas, porque cada um exige uma resposta técnica diferente:

| Código | Problema | Consequência | Resposta do projeto |
|---|---|---|---|
| P1 | **Fragmentação.** Extratos de tag, cartão de combustível, notas fiscais, notas de oficina, multas e apólices chegam em formatos e fontes diferentes. | Ninguém vê o custo total da operação (TCO) sem trabalho manual. | Ingestão multiformato com rastreabilidade ([ingestão e qualidade](ingestao-qualidade.md)) |
| P2 | **Falta de normalização.** Valor absoluto não indica eficiência; sem quilometragem e contexto não existe R$/km comparável. | Comparações injustas entre veículos e frotas diferentes. | Indicadores normalizados e regras de comparabilidade ([diagnóstico](diagnostico.md), [benchmarks](benchmarks.md)) |
| P3 | **Confusão entre volume e ineficiência.** Um custo alto pode vir de rodar mais, pagar mais caro ou consumir mais. | Ações erradas, como cortar viagens rentáveis. | Decomposição do custo em atividade, intensidade e preço ([benchmarks](benchmarks.md)) |
| P4 | **Diagnóstico sem ação.** Relatórios mostram problemas, mas não estimam R$, prioridade nem próximo passo, e ninguém mede o resultado depois. | Análise que não vira decisão. | Economia por cenário, priorização e medição da economia realizada ([economia e recomendações](economia-recomendacoes.md)) |
| P5 | **Dados incompletos desde o primeiro uso.** O gestor raramente tem todos os documentos à mão. | Ferramentas que exigem tudo antes de mostrar algo são abandonadas. | Estimativa progressiva com faixa e perguntas guiadas ([diagnóstico](diagnostico.md#5-estimativa-progressiva-e-perguntas-guiadas)) |

Para a Sem Parar Empresas, o briefing explica por que a calculadora "vira produto" **[Briefing, p. 2]**: gera lead qualificado para o comercial, o benchmark melhora com escala, o gestor volta todo mês para atualizar e o relatório fica pronto para o CFO. Esses quatro pontos aparecem como User Stories da visão Sem Parar Empresas e são tratados em [User Stories](user-stories.md).

## 3. Objetivos

**Objetivo do desafio [Briefing, p. 2]:** "Uma ferramenta que diagnostica o custo total da frota, identifica ineficiências e entrega um plano de ação com economia estimada em R$ — conectando cada recomendação a soluções reais do portfólio Sem Parar Empresas."

**Entregável esperado ao final do projeto [Briefing, p. 2]:** "Aplicação funcional testada com gestores reais, com relatório exportável e recomendações conectadas ao portfólio SPE — entregue ao final de 8 meses."

**Objetivo desta Sprint [Decisão]:** especificar a solução com profundidade suficiente para que as próximas Sprints implementem sem redefinir o problema: produto, dados, métodos de cálculo, arquitetura, segurança, plano de trabalho e critérios de validação, todos rastreados às 20 User Stories.

Metas propostas para validar nas próximas Sprints **[Decisão — metas a confirmar com a Sem Parar Empresas]**:

| Meta | Indicador | Valor proposto | Como medir |
|---|---|---|---|
| Valor no primeiro uso | Tempo até a primeira estimativa de custo total | até 5 minutos, com até 5 perguntas | Teste de usabilidade com gestores (Sprint 4) |
| Diagnóstico confiável | Parcela do custo total apoiada em dado observado após o primeiro envio de documentos | acima de 70% | Dimensão C do índice de confiabilidade |
| Extração útil | Campos monetários extraídos sem correção humana | precisão de 98% nos campos de valor | Amostra rotulada de documentos (Sprint 3) |
| Estimativa honesta | Cobertura da faixa P10-P90 em testes com dados mascarados | entre 70% e 90% | Backtest descrito em [validação](validacao.md) |
| Recorrência | Gestores que atualizam os dados no mês seguinte | a definir com a Sem Parar Empresas | Telemetria de uso do produto |

## 4. Escopo da Sprint 1

| Entregue nesta Sprint | Fora do escopo desta Sprint |
|---|---|
| Documentação de problema, personas, User Stories, solução, dados, métodos, arquitetura, segurança, roadmap e validação | Aplicação funcional (prevista para as Sprints 2 a 4) |
| Modelo conceitual e dicionário de dados (181 campos) | Banco de dados implantado |
| Massa de dados sintéticos com 34 cenários e gabarito | Dados reais de clientes |
| Scripts que recalculam todos os exemplos numéricos ([src/](../src/)) | Modelo de IA treinado ou validado |
| Diagramas em Mermaid, wireframes conceituais e roteiro do vídeo | Interface funcional e integrações por API |

Os scripts em `src/` não são a aplicação. Eles existem para que cada número citado na documentação possa ser reproduzido e conferido.

## 5. Origem dos requisitos

| Requisito | Origem | Situação |
|---|---|---|
| 20 User Stories (gestor de frota, CFO e liderança, Sem Parar Empresas) | [Briefing, p. 3-4] | Todas rastreadas em [User Stories](user-stories.md) |
| Princípios: Simples, Confiável, Flexível, Progressivo | [Briefing, p. 2] | Traduzidos em decisões de produto em [solução](solucao.md#4-princípios-do-briefing-e-como-o-produto-os-cumpre) |
| Fluxo: entrada flexível, diagnóstico, plano de ação | [Briefing, p. 2] | Mapeado nas capacidades do produto |
| Repositório no padrão do template, com README, `data/`, `docs/`, `notebooks/` e `src/` | [Template] | Atendido |
| Decisão sobre participação no FIAP NEXT, campo obrigatório do README | [Template] | **[Pendência]** do grupo |
| Repositório privado, compartilhado apenas com o perfil `fiap-tutoria` | [Enunciado, 4.1] | Repositório privado; acesso de `fiap-tutoria` **[Pendência]** |
| Vídeo de até 5 minutos, com narração humana, no YouTube como não listado, com link no README e no `.txt` | [Enunciado, 4.1] | Roteiro pronto; gravação **[Pendência]** |
| Arquivo `.txt` com os links do repositório e do vídeo, único arquivo enviado no portal | [Enunciado, 4.1] | Preparado; link do vídeo **[Pendência]** |
| Entregáveis do enunciado oficial da Sprint 1 (itens 3 e 4) | [Enunciado] | Conferidos item a item em [validação](validacao.md#6-conferência-com-o-enunciado-oficial) |
| README concentrando todas as informações pedidas | [Enunciado, 4.1] | Atendido: seções 1 a 13 da descrição do [README](../README.md) |
| Responsabilidades definidas para todos os integrantes | [Enunciado, 4.2] | Atendido: um papel por integrante em [roadmap](roadmap.md#3-equipe-e-responsabilidades) |
| Kanban, preferencialmente no Trello | [Enunciado, 3 e 4.1] | Cartões prontos para importar; quadro no Trello **[Pendência]** |

## 6. Premissas e restrições

- **Sem dados reais.** Toda análise usa a massa sintética de `data/sintetico/`. Nenhum registro corresponde a empresa, veículo ou pessoa real; CNPJ e placa não foram gerados.
- **Sem benchmarks proprietários.** O projeto não presume acesso a dados da Sem Parar Empresas. A hierarquia de referências começa pelo histórico da própria frota ([benchmarks](benchmarks.md)).
- **Parâmetros de mercado são hipóteses.** Preços, consumos e custos usados na simulação estão em [`data/parametros-simulacao.csv`](../data/parametros-simulacao.csv) com o tipo de cada valor: hipótese de simulação, valor legal ou convenção.
- **Base legal verificada por busca.** Os dispositivos legais citados (CTB, LGPD, Vale-Pedágio, eixo suspenso) foram conferidos por mecanismo de busca e fontes secundárias; o texto oficial no Planalto estava bloqueado neste ambiente. Ver [referências](referencias.md).
- **Sem pesquisa com usuários.** As personas são hipotéticas e derivadas do briefing ([personas](personas.md)).

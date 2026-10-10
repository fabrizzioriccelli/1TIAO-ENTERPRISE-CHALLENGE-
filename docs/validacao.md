# Validação, revisão técnica e matriz de conclusão

Este documento separa três coisas que não podem ser confundidas: o que foi **verificado por script**, o que exige **conferência humana** e o que está **pendente** de ação do grupo ou de terceiros.

## 1. Como reproduzir

```bash
python src/gerar_dados_sinteticos.py
python src/exemplos_calculados.py
python src/validar_entregaveis.py --reproduzir --mmdc CAMINHO/mmdc --puppeteer-config CAMINHO/puppeteer.json
```

O validador grava o [relatório completo](anexos/relatorio-validacao.md) e termina com erro se houver alguma falha. Sem o mermaid-cli, a verificação dos diagramas aparece como aviso, não como aprovação.

## 2. Verificações automáticas

Execução de 9 out. 2026, com mermaid-cli e regeneração da massa sintética. O resultado detalhado, linha a linha, está no [relatório](anexos/relatorio-validacao.md).

| Grupo | O que confere | Resultado |
|---|---|---|
| Dicionário | 13 atributos por campo, sem duplicidade; colunas dos 14 CSVs iguais às do dicionário em nome e ordem | Aprovado. 3 campos de texto livre sem regra de máquina (aviso aceito: não há formato a validar) |
| Regras de máquina | Tipo, obrigatoriedade, domínio, expressão regular, chave primária e estrangeira, limites, aplicados a todos os registros | Aprovado. As violações encontradas estão todas em registros de cenários do gabarito; nenhuma fora dele |
| Gabarito | G01 a G34, registros referenciados existem, contagens de `metadados.json` | Aprovado |
| Links e âncoras | Arquivos e âncoras de todos os links internos dos Markdown, com a regra de âncora do GitHub | Aprovado |
| Tabelas Markdown | Mesma quantidade de células por linha e linha separadora válida | Aprovado |
| Mermaid | Renderização de cada diagrama com mermaid-cli | Aprovado (9 diagramas, incluindo o fluxo do README) |
| Números | Valores-chave do README e dos documentos contra o JSON calculado; valores com centavos dos documentos procurados no anexo | Aprovado |
| Dados sensíveis | CPF, CNPJ, placa real, e-mail, chaves e senhas em todos os arquivos de texto | Aprovado. Nenhuma ocorrência |
| Arquivos | Duplicados, codificação UTF-8, emojis fora dos títulos do template | Aprovado |
| Template e entrega | Seções do README, observação do tutor removida, itens do enunciado, campo FIAP NEXT, pastas, arquivo de links | Aprovado |
| Reprodutibilidade | Massa regenerada idêntica byte a byte à versionada | Aprovado |

**O validador também foi testado.** Em uma cópia do repositório, foram injetados seis tipos de erro: link e âncora inexistentes, tabela com célula a mais, CPF, e-mail e placa no texto, categoria inválida em uma despesa fora do gabarito, número divergente no README e emoji em um documento. **Os seis foram detectados.**

**Desempenho.** O núcleo do cálculo (carregar, validar e calcular IND-01 a IND-05 das três frotas, 21.656 despesas) leva cerca de 0,9 s; o script completo de exemplos, cerca de 4 s. A medição está em [arquitetura](arquitetura.md) (RNF-06) e não é teste de carga.

## 3. Verificações manuais e pendentes

| Verificação | Situação | Observação |
|---|---|---|
| Links externos | **Manual** | 12 endereços distintos (inclui os perfis do GitHub dos integrantes); a rede do ambiente bloqueava a maioria. Abrir cada um antes da entrega |
| Referências legais e bibliográficas | **Parcial** | Conferidas por busca; nível indicado em [referências](referencias.md). Itens marcados como pendentes precisam do texto original |
| Ortografia e clareza | **Parcial** | Revisão assistida durante a escrita; falta leitura humana completa (K-021) |
| Visual dos wireframes e gráficos | **Verificado** | Imagens geradas e inspecionadas; problemas encontrados corrigidos (ver auditoria) |
| Contraste de cores | **Verificado** | Calculado pela fórmula da WCAG; ver [UX](ux-identidade-visual.md#2-tokens) |
| Repositório privado e acesso do `fiap-tutoria` | **Pendente** | Visibilidade a confirmar na página do repositório; acesso do tutor depende do dono (K-020) |
| Enunciado oficial no portal | **Verificado** | Texto transcrito pelo grupo; conferência na seção 6 |
| Vídeo | **Manual** | Publicado como não listado (https://youtu.be/MD6aKeIHl-Y); o link foi informado pelo grupo e não pôde ser aberto neste ambiente. Testar em janela anônima |

## 4. Revisão técnica em cinco perspectivas

Cada perspectiva leu os entregáveis com uma pergunta. Os achados abaixo são reais, encontrados durante a produção ou nesta revisão; o status indica o que foi feito.

| Código | Perspectiva | Achado | Status |
|---|---|---|---|
| AUD-01 | Banca FIAP: o template foi seguido? | README ainda era a cópia do template, com a observação do tutor | **Corrigido**: seções preenchidas; integrantes e tutor informados pelo grupo |
| AUD-02 | Banca FIAP | Âncoras de links sem acento não funcionam no GitHub | **Corrigido**: âncoras com acento, conferidas pelo validador |
| AUD-03 | Banca FIAP | Diagrama de sequência com `;` em mensagem não renderizava | **Corrigido**: os 9 diagramas renderizam |
| AUD-04 | Banca FIAP | Contagem de campos por grupo do dicionário divergia do arquivo | **Corrigido** |
| AUD-05 | Sem Parar Empresas: a solução é útil e honesta comercialmente? | ROI inicial acima de 2.000%, calculado só sobre a implantação | **Corrigido**: ROI sobre custo total, com custo de operar o plano e cenários por evidência |
| AUD-06 | Sem Parar Empresas | O fator "base" da hipótese OP-C4 parecia contradizer a escada de evidência | **Corrigido**: explicação em [economia](economia-recomendacoes.md#3-cenários-escada-de-evidência) |
| AUD-07 | Sem Parar Empresas | O catálogo de associação ao portfólio não foi validado pela empresa | **Pendente** (K-205, Sprint 3) |
| AUD-08 | Sem Parar Empresas | US-SP-06 lida literalmente conflita com a LGPD | **Aceito por decisão**: atendimento com autorização, registrado como parcial |
| AUD-09 | Usuário (gestor e CFO): os números merecem confiança? | Detector de queda usava a variação entre veículos e só achava 1 de 3 casos | **Corrigido**: variação do próprio veículo; 3 de 3, sem alarme falso |
| AUD-10 | Usuário | Estimativa de manutenção com cobertura mal definida e subestimação de custos concentrados | **Corrigido**: modelo de frequência e severidade com cobertura declarada |
| AUD-11 | Usuário | No N3, o valor real ficou fora da faixa | **Aceito e documentado**: backtest mostrou viés e, depois de calibrar, faixa larga demais; critério de aceite na Sprint 3 |
| AUD-13 | Usuário | Cinza de legendas com contraste 3,50:1, abaixo da WCAG | **Corrigido**: `#6f6e69`, 4,98:1 |
| AUD-14 | Usuário | Wireframes com decimais em formato americano | **Corrigido** |
| AUD-15 | Engenharia e dados: o que está escrito é reproduzível? | Gerador com falhas (multas atribuídas à empresa errada, reabastecimentos fora de ordem, passagens repetidas em minutos, falsos positivos de data futura) | **Corrigido**; massa regenerada idêntica |
| AUD-16 | Engenharia e dados | Requisito de desempenho citava tempo sem dizer o que foi medido | **Corrigido**: medição descrita na RNF-06 |
| AUD-17 | Engenharia e dados | `despesas.veiculo_id` sem regra de máquina | **Corrigido**: chave estrangeira; violações só nos registros do cenário G18 |
| AUD-18 | Engenharia e dados | Regras testadas com erros que os autores conheciam | **Limitação declarada**: prova a mecânica, não o desempenho |
| AUD-19 | Jurídico, LGPD e ética: o projeto expõe alguém ou promete demais? | Leis conferidas apenas por busca | **Pendente**: validação jurídica antes do piloto (RSK-07) |
| AUD-20 | Jurídico, LGPD e ética | Risco de linguagem de promessa de economia | **Verificado**: busca por termos de garantia não encontrou promessas; regra de bloqueio na [estratégia de IA](estrategia-ia.md#3-verificação-numérica-de-textos-gerados) |
| AUD-22 | Jurídico, LGPD e ética | Dados pessoais ou reais no repositório | **Verificado**: varredura sem ocorrências; placas, condutores e apólices pseudonimizados |

## 5. Matriz de critérios de conclusão

Status: **Atendido**, **Parcialmente atendido**, **Pendente** ou **Não aplicável**. "Pendente" aqui significa que depende do grupo ou de terceiros, não de trabalho técnico não feito.

| # | Critério | Status | Evidência ou motivo |
|---|---|---|---|
| 1 | Análise do problema e dos requisitos, separando briefing, decisão e pendência | Atendido | [problema.md](problema.md) |
| 2 | Visão do produto com as cinco capacidades | Atendido | [solucao.md](solucao.md#3-cinco-capacidades) |
| 3 | Diferenciais avaliados (incluídos e descartados) | Atendido | [solucao.md](solucao.md#6-diferenciais-avaliados) |
| 4 | Rastreabilidade das 20 User Stories, com MoSCoW, critério de aceite e Sprint | Atendido | [user-stories.md](user-stories.md) |
| 5 | Personas hipotéticas, sem entrevistas inventadas | Atendido | [personas.md](personas.md); roteiro de entrevista para a Sprint 4 |
| 6 | Modelo conceitual e dicionário com os atributos exigidos | Atendido | [modelagem-dados.md](modelagem-dados.md), [dicionário](../data/dicionario-dados.csv) |
| 7 | Dados sintéticos com hipóteses documentadas | Atendido | [modelagem-dados.md](modelagem-dados.md#5-massa-de-dados-sintéticos), [parâmetros](../data/parametros-simulacao.csv) |
| 8 | Pipeline de ingestão e qualidade, da recepção à análise | Atendido (especificação) | [ingestao-qualidade.md](ingestao-qualidade.md) |
| 9 | Indicadores com os dez atributos | Atendido | [diagnostico.md](diagnostico.md#3-indicadores) (IND-01 a IND-12) |
| 10 | Taxonomia da observação à economia realizada | Atendido | [diagnostico.md](diagnostico.md#2-da-observação-à-economia-realizada) |
| 11 | Indicador de confiança com cinco dimensões, sem chamá-lo de probabilidade | Atendido | [diagnostico.md](diagnostico.md#6-índice-de-confiabilidade) |
| 12 | Hierarquia de benchmarks e regras de comparabilidade | Atendido | [benchmarks.md](benchmarks.md) |
| 13 | Metodologia de economia: bruta e líquida, payback, ROI, três cenários, sem dupla contagem, sem promessas | Atendido | [economia-recomendacoes.md](economia-recomendacoes.md) |
| 14 | Priorização e próximo passo | Atendido | [economia-recomendacoes.md](economia-recomendacoes.md#5-priorização-e-próximo-passo) |
| 15 | Recomendações associadas ao portfólio de forma contextual | Parcialmente atendido | Catálogo pronto; validação pela Sem Parar Empresas pendente (AUD-07) |
| 16 | Estratégia de IA por componente, sem cálculo financeiro por modelo de linguagem | Atendido | [estrategia-ia.md](estrategia-ia.md) |
| 17 | Arquitetura modular e pelo menos cinco diagramas | Atendido | [arquitetura.md](arquitetura.md); 9 diagramas Mermaid (um deles no README) e 7 SVG |
| 18 | Segurança e LGPD | Parcialmente atendido | [seguranca-lgpd.md](seguranca-lgpd.md); validação jurídica pendente (AUD-19) |
| 19 | UX e identidade visual sem emojis, gradientes ou logos alterados | Atendido | [ux-identidade-visual.md](ux-identidade-visual.md) |
| 20 | Repositório organizado conforme o template | Atendido | Estrutura, seções, integrantes, tutor e decisão sobre o FIAP NEXT completos; o grupo não adotou nome |
| 21 | Roadmap, papéis, RACI e Kanban sem itens concluídos sem evidência | Atendido | [roadmap.md](roadmap.md), [kanban.csv](anexos/kanban.csv) |
| 22 | Animação do vídeo de até 5 minutos | Atendido | Animação de 4:45 com narração humana |
| 23 | Vídeo gravado e publicado | Atendido | Narração humana sobre a animação, publicado como não listado: https://youtu.be/MD6aKeIHl-Y (K-022, K-023) |
| 24 | Arquivo .txt com os links do repositório e do vídeo | Atendido | [arquivo](../ENTREGA_SPRINT1_LINKS.txt) com os dois links |
| 25 | Entrega do .txt no portal | Pendente | Ação do grupo (K-025) |
| 26 | Revisão técnica em cinco perspectivas | Atendido | Seção 4 deste documento |
| 27 | Verificações executadas, separando verificado, manual e pendente | Atendido | Seções 2 e 3 e [relatório](anexos/relatorio-validacao.md) |
| 28 | Teste adversarial com 15 perguntas ou mais | Atendido | [teste-adversarial.md](teste-adversarial.md) (19 perguntas) |
| 29 | Repositório privado, sem dados reais nem credenciais | Atendido | Varredura sem ocorrências; visibilidade conferida no GitHub |
| 30 | Acesso do perfil `fiap-tutoria` | Pendente | Concessão pelo dono do repositório (K-020) |
| 31 | Nome do grupo, integrantes e tutor | Atendido | Integrantes com RM e GitHub, tutora e coordenador no README; o grupo não adotou nome e retirou a seção "Nome do grupo" (K-018) |
| 32 | Decisão sobre o FIAP NEXT | Atendido | "Sim, aceitamos participar", com nome e RM dos integrantes (K-019) |
| 33 | Conferência com o enunciado oficial do portal | Atendido | Seção 6 deste documento (K-024) |
| 34 | Aplicação funcional | Não aplicável | Fora do escopo da Sprint 1 (especificação); prevista nas Sprints 2 a 4 |
| 35 | Testes com gestores reais | Não aplicável | Previstos para a Sprint 4 |
| 36 | README concentrando todas as informações do enunciado | Atendido | Seções 1 a 14 da descrição do README |
| 37 | Responsabilidades definidas para cada integrante | Atendido | Um papel por integrante no README e no [roadmap](roadmap.md#3-equipe-e-responsabilidades), também usado na divisão do vídeo |
| 38 | Kanban no Trello ou ferramenta semelhante | Parcialmente atendido | [kanban.csv](anexos/kanban.csv) pronto para importar; quadro a criar pelo grupo |

## 6. Conferência com o enunciado oficial

Enunciado da atividade transcrito pelo grupo em 9 out. 2026. Cada entregável do item 4.1 foi conferido contra o README, que deve concentrar todas as informações.

| Entregável do enunciado (4.1) | Onde está | Status |
|---|---|---|
| Descrição do problema e entendimento do desafio | README, seção 1; [problema.md](problema.md) | Atendido |
| User Stories selecionadas, com explicação de como a solução responde a cada uma | README, seção 4; [user-stories.md](user-stories.md) | Atendido (as 20) |
| Definição da solução: o que faz, quem usa, benefícios por perfil | README, seção 3; [solucao.md](solucao.md) | Atendido |
| Usuários e necessidades (gestor, CFO e liderança, Sem Parar Empresas) | README, seção 2; [personas.md](personas.md) | Atendido |
| Estruturação dos dados, com exemplos e significado das variáveis | README, seção 5; [dicionário](../data/dicionario-dados.csv) | Atendido (dados simulados) |
| Estratégia de entrada de dados por formato | README, seção 6; [ingestao-qualidade.md](ingestao-qualidade.md) | Atendido |
| Proposta de diagnóstico e priorização dos custos | README, seção 7; [diagnostico.md](diagnostico.md) | Atendido |
| Recomendações e plano de ação, com relação ao portfólio | README, seção 8; [economia-recomendacoes.md](economia-recomendacoes.md) | Atendido |
| Tratamento de dados incompletos | README, seção 9 | Atendido |
| Orientação ao usuário sobre dados faltantes | README, seção 10 | Atendido |
| Diagrama da arquitetura com o fluxo entrada → tratamento → análise → diagnóstico → benchmark → recomendações → visualização/relatório | README, seção 11; [arquitetura.md](arquitetura.md) | Atendido |
| Planejamento: atividades, responsabilidades dos integrantes, etapas e Kanban | README, seção 13; [roadmap.md](roadmap.md) | Parcialmente atendido: papéis distribuídos; falta criar o quadro no Trello |
| Vídeo de até 5 minutos com narração humana, não listado, link no README | README, "Links do Projeto" | Atendido: https://youtu.be/MD6aKeIHl-Y |
| README organizado com todas as informações | README | Atendido |

Requisitos técnicos dos itens 3.1 a 3.10, todos tratados nos documentos: formatos de entrada, variáveis e categorias, dataset simulado, extração e validação, dados incompletos (3.2); ineficiências e indicadores (3.3); IA com entradas, saídas e justificativa, sem modelo treinado (3.4); ações priorizadas e portfólio (3.5); relatório exportável e atualização periódica (3.6); fluxo, componentes, integrações e separação entre dados, análise, regras e interface (3.7); autenticação, integridade, dados de contato e privacidade (3.8); simulação coerente (3.9); relação explícita com as User Stories e justificativas (3.10).

**Regras gerais (4.2) que dependem do grupo:**

- O repositório deve ser privado e **compartilhado apenas com `fiap-tutoria`**. Hoje ele é privado e não tem outros colaboradores; falta convidar `fiap-tutoria`, que precisa aceitar o convite.
- O repositório **não pode ser alterado depois da data limite**.
- Todos os integrantes devem contribuir e ter responsabilidades definidas.

## 7. Parecer

A documentação técnica da Sprint 1 está completa e passou nas verificações automáticas. O que falta não é técnico: quadro no Trello, acesso do `fiap-tutoria`, gravação e publicação do vídeo e, principalmente, a **revisão do grupo**. Sem essa revisão, o grupo não terá domínio do conteúdo para responder à banca, e nenhum cartão deve sair de "Em revisão".

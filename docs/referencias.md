# Referências

Formato inspirado na ABNT NBR 6023. Data de acesso de todas as fontes on-line: **9 out. 2026**.

**Nível de verificação.** Este ambiente de trabalho bloqueava o acesso direto à maior parte dos sites oficiais (Planalto, gov.br, Câmara, ISO, Crossref). Por isso cada referência informa como foi conferida:

| Nível | Significado |
|---|---|
| **Documento** | O documento foi lido diretamente (briefing em PDF, repositório do template) |
| **Busca** | Dados conferidos em resultados de mecanismo de busca e fontes secundárias concordantes; o texto original não foi aberto |
| **Pendente** | Precisa de conferência no texto original antes de uso em produção ou em material externo |

Os dispositivos legais são citados para orientar requisitos de produto. **Não constituem parecer jurídico**: devem ser validados por profissional habilitado e conferidos na redação vigente do Planalto antes do piloto (risco RSK-07 do [roadmap](roadmap.md#5-riscos-do-projeto)).

## 1. Material oficial do desafio

| Referência | Uso no projeto | Verificação |
|---|---|---|
| SEM PARAR EMPRESAS. *Enterprise Challenge: Calculadora de Redução de Custos de Frota*. Briefing em PDF, 4 p. Fornecido pela FIAP, 2026. | Problema, números do negócio, portfólio, princípios e as 20 User Stories | Documento |
| FIAP. *FIAP-PORTFOLIO-AI*: template de repositório. Disponível em: https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI. | Estrutura do repositório e do README | Documento |
| FIAP. *Challenge Sem Parar: Sprint 1*. Enunciado da atividade no Portal do Aluno (on.fiap.com.br, atividade 662294). 2026. | Objetivos, requisitos técnicos e entregáveis da Sprint 1 | Documento: texto transcrito pelo grupo em 9 out. 2026 (o portal exige login) |
| CORPAY. Comunicados sobre a mudança de nome de FleetCor Technologies para Corpay (2024) e sobre a aquisição da Sem Parar (2016). | Contexto institucional | Busca |

## 2. Legislação e regulação

| Referência | Dispositivos usados | Verificação |
|---|---|---|
| BRASIL. Lei nº 9.503, de 23 de setembro de 1997. Código de Trânsito Brasileiro. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm. | Art. 257, §§ 7º e 8º (prazo de 30 dias para indicar o condutor e multa NIC); art. 258 (valores por natureza da infração); art. 284 (desconto de 20%, ou 40% com o sistema de notificação eletrônica) | Busca |
| BRASIL. Lei nº 14.071, de 13 de outubro de 2020. Altera o Código de Trânsito Brasileiro. | Redação do prazo de indicação do condutor | Busca |
| BRASIL. Lei nº 14.229, de 21 de outubro de 2021. Altera o Código de Trânsito Brasileiro. | Redação do valor da multa por não indicação do condutor | Busca |
| BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. | Arts. 6º, 7º, 10, 12, 18, 33, 37 e 38 | Busca |
| BRASIL. Lei nº 10.209, de 23 de março de 2001. Institui o Vale-Pedágio obrigatório. | Obrigação do embarcador e indenização de duas vezes o valor do frete (art. 8º); ver também o julgamento da ADI 6031 pelo STF | Busca; **Pendente** quanto aos efeitos da ADI 6031 |
| BRASIL. Lei nº 13.103, de 2 de março de 2015. Lei do Motorista. Art. 17, com redação da Lei nº 13.711/2018. | Isenção de pedágio sobre eixos suspensos de veículos vazios | Busca |
| BRASIL. Lei nº 13.703, de 8 de agosto de 2018. Política Nacional de Pisos Mínimos do Transporte Rodoviário de Cargas. | Contexto de custo de frete (ANTT) | Busca |
| ANPD. *Guia orientativo para definições dos agentes de tratamento de dados pessoais e do encarregado*. Versão 2.0, 2022. | Papéis de controlador e operador | Busca |
| ANPD. *Guia orientativo: hipóteses legais de tratamento de dados pessoais: legítimo interesse*. Fev. 2024. | Base legal das finalidades comerciais | Busca |
| ANP. *Levantamento de Preços de Combustíveis* (série histórica). Disponível no portal gov.br/anp. | Referência externa de preço (IND-08) | Busca |
| BRASIL. Nota Fiscal Eletrônica: leiaute da NF-e, grupo de combustíveis (`comb`, campo `cProdANP`). Portal Nacional da NF-e. | Classificação de combustível na ingestão | Busca |
| CONTRAN. Padrão de placas de identificação veicular (modelo Mercosul). | Expressão regular de validação de placas | **Pendente**: número e redação da resolução vigente não conferidos |

## 3. Métodos quantitativos

| Referência | Uso no projeto | Verificação |
|---|---|---|
| ANG, B. W. The LMDI approach to decomposition analysis: a practical guide. *Energy Policy*, v. 33, n. 7, p. 867-871, 2005. | Decomposição do custo de combustível em atividade, intensidade e preço | Busca |
| IGLEWICZ, B.; HOAGLIN, D. C. *How to detect and handle outliers*. Milwaukee: ASQC Quality Press, 1993. | Z modificado (constante 0,6745 e limiar 3,5) | Busca |
| PAGE, E. S. Continuous inspection schemes. *Biometrika*, v. 41, n. 1-2, p. 100-115, 1954. DOI: 10.1093/biomet/41.1-2.100. | CUSUM para detectar queda de rendimento | Busca |
| LIU, F. T.; TING, K. M.; ZHOU, Z.-H. Isolation forest. In: IEEE INTERNATIONAL CONFERENCE ON DATA MINING (ICDM), 8., 2008, Pisa. *Proceedings* [...]. p. 413-422. DOI: 10.1109/ICDM.2008.17. | Alternativa para anomalias multivariadas, fora do MVP | Busca |
| HYNDMAN, R. J.; ATHANASOPOULOS, G. *Forecasting: principles and practice*. 3. ed. Melbourne: OTexts, 2021. Disponível em: https://otexts.com/fpp3/. | Avaliação de previsões e intervalos | Busca |
| EFFICIENCY VALUATION ORGANIZATION (EVO). *International Performance Measurement and Verification Protocol (IPMVP)*. | Lógica de linha de base ajustada para medir economia realizada | Busca |
| SWEENEY, L. k-anonymity: a model for protecting privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, v. 10, n. 5, p. 557-570, 2002. | Tamanho mínimo de grupo em benchmarks entre clientes | Busca |

Os modelos de estimativa (simulação de Monte Carlo com distribuições triangulares, frequência e severidade com Gamma-Poisson e lognormal, valor da informação) são formulações do próprio grupo sobre técnicas estatísticas padrão. As premissas numéricas estão em [`data/parametros-simulacao.csv`](../data/parametros-simulacao.csv) e **não** vêm de fonte externa: são hipóteses a calibrar com dados reais.

## 4. Produto, qualidade e experiência

| Referência | Uso no projeto | Verificação |
|---|---|---|
| AGILE BUSINESS CONSORTIUM. *DSDM Agile Project Framework*: MoSCoW prioritisation. Técnica atribuída a Dai Clegg. | Priorização das User Stories | Busca |
| McBRIDE, S. RICE: simple prioritization for product managers. *Intercom Blog*. | Base da fórmula de prioridade das oportunidades | Busca |
| ISO; IEC. *ISO/IEC 25012:2008*: Software engineering: Software product Quality Requirements and Evaluation (SQuaRE): Data quality model. Genebra, 2008. | Dimensões do indicador de confiabilidade | Busca |
| W3C. *Web Content Accessibility Guidelines (WCAG) 2.2*. Disponível em: https://www.w3.org/TR/WCAG22/. | Meta de acessibilidade; critério 1.4.3 (contraste de 4,5:1) | Busca |
| BROOKE, J. SUS: a "quick and dirty" usability scale. In: JORDAN, P. W. et al. (ed.). *Usability evaluation in industry*. London: Taylor & Francis, 1996. p. 189-194. | Medida de usabilidade nos testes da Sprint 4 | Busca |

## 5. Segurança

| Referência | Uso no projeto | Verificação |
|---|---|---|
| OWASP. *Application Security Verification Standard (ASVS)* 5.0.0. Maio 2025. | Lista de verificação nível 2 | Busca |
| NIST. *SP 800-63B-4: Digital Identity Guidelines: Authentication and Authenticator Management*. Gaithersburg: NIST, 2025. | Política de senhas (mínimo de 15 caracteres quando a senha é o único fator) | Busca |

## 6. Ferramentas citadas

| Ferramenta | Uso |
|---|---|
| Python, pandas e NumPy | Geração da massa sintética, cálculos de exemplo e gráficos SVG (escritos diretamente, sem biblioteca de gráficos) |
| Mermaid e mermaid-cli | Diagramas em texto e verificação de sintaxe |
| Chromium sem interface | Captura dos wireframes e impressão dos slides |
| Tesseract OCR (https://github.com/tesseract-ocr/tesseract) | Alternativa de extração a avaliar na Sprint 3 |
| FastAPI e PostgreSQL | Pilha proposta para o produto ([arquitetura](arquitetura.md)) |

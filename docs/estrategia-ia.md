# Estratégia de inteligência artificial

**Nesta Sprint não existe modelo treinado nem validado.** Este documento define onde a IA agrega valor, com que técnica, como será avaliada e em que Sprint entra. A regra central: **a IA apoia leitura, classificação e comunicação; cálculos financeiros são determinísticos, reproduzíveis e versionados.**

## 1. Princípios

1. **Método mais simples que resolve.** Regras e estatística robusta vêm antes de modelos complexos; um modelo só substitui uma regra se superá-la na mesma avaliação.
2. **Linguagem natural não calcula.** Um modelo de linguagem pode redigir uma explicação, mas cada número do texto precisa existir no resultado calculado. Texto com número não verificável é descartado.
3. **Pessoa no circuito.** Baixa confiança leva a revisão humana. Achados viram oportunidades validadas por confirmação do gestor ou por regra determinística.
4. **Documento é dado, não instrução.** Texto extraído de PDFs e imagens é tratado como conteúdo não confiável. Um documento com "ignore as instruções anteriores" não altera o comportamento do sistema; o modelo não tem permissão para executar ações.
5. **Avaliação antes de produção.** Cada componente tem conjunto de teste, métrica e limiar de aceite definidos antes do desenvolvimento.
6. **Privacidade.** Dados de clientes não treinam modelos sem autorização específica. Se for usado serviço externo de IA, o contrato deve vedar retenção e treinamento com os dados, e a transferência internacional deve seguir a LGPD ([segurança e LGPD](seguranca-lgpd.md)).

## 2. Componentes

### IA-01 Extração documental

| Atributo | Especificação |
|---|---|
| Problema | Transformar PDF escaneado, foto, print e texto livre em registros estruturados (US-GF-01) |
| Entrada | Arquivo bruto; esquema esperado por tipo de documento (nota de oficina, comprovante de pedágio, apólice) |
| Saída | Campos (data, valor, litros, placa, fornecedor, itens) com confiança por campo e localização no documento |
| Técnica candidata | (a) OCR de código aberto (Tesseract, com modelo em português) mais regras de leiaute; (b) serviço de extração de documentos em nuvem; (c) modelo multimodal com saída em esquema JSON. Todas seguidas de validação determinística |
| Justificativa | Documentos heterogêneos e de baixa qualidade são o principal obstáculo ao "qualquer formato entra" do briefing |
| Dados necessários | Amostra rotulada de, no mínimo, 200 documentos por tipo, de clientes que autorizarem ou sintéticos; o conjunto cresce com as correções humanas |
| Limitações | Fotos ruins; leiautes novos; caligrafia |
| Riscos | Valor errado que passa sem revisão; vazamento de dados para fornecedor externo; injeção de instruções em documentos |
| Métricas | Precisão e cobertura por campo; taxa de erro por caractere (OCR); **precisão de 98% nos campos monetários** aceitos sem revisão; percentual processado sem intervenção |
| Revisão humana | Campo abaixo de 0,80; soma dos itens diferente do total; valor fora da faixa plausível |
| Momento | Sprint 3: comparação das três alternativas na mesma amostra, com escolha documentada |

### IA-02 Classificação de despesas

| Atributo | Especificação |
|---|---|
| Problema | Atribuir categoria e subcategoria a cada lançamento |
| Entrada | Descrição original, fornecedor, códigos fiscais (como o código de produto da ANP na NF-e de combustível), valor e origem |
| Saída | Categoria, subcategoria e confiança |
| Técnica candidata | Regras e dicionários primeiro (códigos fiscais, palavras-chave, tipo de fornecedor). Depois, um classificador simples (regressão logística sobre TF-IDF, ou árvores de gradiente) para descrições livres, só se superar as regras |
| Justificativa | A maioria dos lançamentos vem de extratos com categoria implícita; o modelo resolve a cauda de descrições livres |
| Dados necessários | Lançamentos rotulados; as correções humanas viram rótulos (aprendizado ativo) |
| Limitações | Descrições curtas e ambíguas ("serviço", "diversos") |
| Riscos | Classe errada desloca custo entre categorias e distorce indicadores |
| Métricas | F1 macro; recall por categoria; cobertura com confiança acima do limiar; matriz de confusão comparada à linha de base por regras |
| Revisão humana | Confiança abaixo do limiar; categoria nova sugerida |
| Momento | Regras na Sprint 2; modelo na Sprint 3, se a avaliação justificar |

### IA-03 Detecção de anomalias

| Atributo | Especificação |
|---|---|
| Problema | Encontrar desvios relevantes sem tratar volume como desperdício (US-GF-03) |
| Entrada | Indicadores normalizados por veículo e mês; referência de pares e histórico |
| Saída | Anomalias com método, magnitude, data de início e confiança |
| Técnica candidata | Regras determinísticas; z modificado entre pares (mediana e MAD); CUSUM sobre a razão em relação aos pares; decomposição LMDI. Isolation Forest (Liu, Ting e Zhou, 2008) só quando houver muitas variáveis por veículo e rótulos de validação |
| Justificativa | Poucos dados por veículo, necessidade de explicar cada alerta e custo baixo de falso alarme mal explicado são favoráveis a métodos estatísticos transparentes |
| Dados necessários | 6 meses de linha de base por veículo; 5 pares por categoria |
| Limitações | Detecta mudança e diferença, não causa; frota pequena tem poucos pares |
| Riscos | Excesso de alertas (fadiga); falsa acusação de condutor |
| Métricas | Na massa sintética: 3 de 3 veículos com queda detectados, sem alarme falso em 40. Em dados reais: precisão entre os primeiros alertas validados pelo gestor; atraso de detecção; alertas por 100 veículos·mês |
| Revisão humana | Toda anomalia é hipótese até confirmação |
| Momento | Sprint 3 |

### IA-04 Estimativas e calibração

| Atributo | Especificação |
|---|---|
| Problema | Estimar o custo total com faixa honesta quando faltam dados (US-GF-09) |
| Entrada | Composição da frota, respostas, documentos, premissas versionadas |
| Saída | P10, P50 e P90 por componente e total; parcela observada; próximas perguntas |
| Técnica candidata | Simulação de Monte Carlo com distribuições triangulares; frequência × severidade com atualização Gamma-Poisson para manutenção; recalibração com dados agregados. Regressão quantílica ou modelos hierárquicos bayesianos quando houver base suficiente |
| Justificativa | Explica de onde vem a incerteza e funciona com pouquíssimos dados |
| Dados necessários | Premissas iniciais (hipóteses) e depois grupos de referência autorizados |
| Limitações | Premissas genéricas criam viés: no backtest sintético, 23,2% dos casos ficaram acima do P90 e 0,7% abaixo do P10 |
| Riscos | Faixa estreita e errada dar falsa segurança |
| Métricas | Cobertura P10-P90 entre 70% e 90%, com erros nas duas caudas; erro mediano do P50; largura relativa por nível |
| Revisão humana | Revisão das premissas a cada recalibração |
| Momento | Sprint 2 (N0 a N2); calibração na Sprint 3 |

### IA-05 Recomendações

| Atributo | Especificação |
|---|---|
| Problema | Transformar achados em ações com economia estimada |
| Entrada | Achados, catálogo REC, premissas de captura e custo |
| Saída | Ações, economia por cenário, prioridade, próximo passo |
| Técnica candidata | Motor de regras auditável (catálogo versionado) e cálculo determinístico. Sem modelo generativo na decisão |
| Justificativa | Recomendações precisam ser explicáveis, reproduzíveis e livres de associação comercial automática |
| Dados necessários | Catálogo validado com a Sem Parar Empresas e com gestores |
| Limitações | Só recomenda o que está no catálogo |
| Riscos | Catálogo enviesado para produtos; promessa implícita de economia |
| Métricas | Taxa de aceite das ações; percentual com economia realizada medida; razão entre realizado e estimado por tipo de ação |
| Revisão humana | Inclusão e alteração de regras passam por revisão do grupo e da Sem Parar Empresas |
| Momento | Sprint 3 |

### IA-06 Linguagem natural (assistente explicativo)

| Atributo | Especificação |
|---|---|
| Problema | Explicar indicadores e achados em linguagem simples, para o gestor e para o CFO |
| Entrada | JSON do diagnóstico (fatos calculados, registros de origem e premissas) |
| Saída | Texto curto com explicação, sempre ligado aos fatos de origem |
| Técnica candidata | Primeiro, textos por modelo (templates) determinísticos. Depois, modelo de linguagem com recuperação restrita ao diagnóstico do próprio cliente e saída verificada |
| Justificativa | Facilita o uso ("sem treinamento, sem manual"), mas não é necessário para o MVP |
| Dados necessários | Diagnósticos de exemplo; avaliação com usuários |
| Limitações | Respostas fora do escopo do diagnóstico |
| Riscos | Alucinação de números, causas ou promessas; vazamento entre clientes |
| Métricas | **100% dos números do texto presentes no JSON do diagnóstico** (verificação automática); taxa de recusa correta fora do escopo; compreensão medida em teste com usuários |
| Revisão humana | Amostragem periódica dos textos gerados |
| Momento | Templates na Sprint 3; modelo de linguagem só depois do MVP |

## 3. Verificação numérica de textos gerados

Exigida para IA-06 e para qualquer texto produzido por modelo:

1. Extrair todos os números do texto (valores, percentuais, datas, quantidades).
2. Comparar cada um com os fatos do diagnóstico, com tolerância de arredondamento.
3. Sem correspondência: descartar o texto e usar o template determinístico.
4. Proibir termos de garantia ("garante", "certamente economizará") por lista de bloqueio.
5. Registrar versão do modelo, prompt e resultado da verificação.

## 4. O que é automático e o que exige pessoa

| Decisão | Automática | Exige pessoa |
|---|---|---|
| Aceitar valor extraído com confiança ≥ 0,80 e coerente | Sim | Auditoria amostral |
| Excluir duplicidade de arquivo ou de transação | Sim | Pode desfazer |
| Imputar litros (IMP-01) | Sim, marcado | - |
| Classificar achado como anomalia | Sim | - |
| Tratar anomalia como ineficiência | Não | Gestor confirma |
| Executar contestação, bloqueio de cartão ou desmobilização | Não | Gestor decide |
| Exibir solução Sem Parar Empresas | Sim, se a regra for satisfeita | Catálogo revisado por pessoas |
| Contato comercial | Não | Só com base legal registrada; sempre por pessoa |

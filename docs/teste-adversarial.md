# Teste adversarial: perguntas difíceis da banca

Perguntas que uma banca exigente faria, respondidas **somente com o que está nos documentos**. Quando a pergunta revelou uma lacuna, a lacuna foi corrigida ou registrada, e isso aparece na coluna "Efeito no projeto" do resumo ao final. Cada integrante deve conseguir responder às perguntas da sua área sem consulta (ver [uso de IA](uso-de-ia.md#5-responsabilidade-do-grupo)).

## Dados e validação

**1. Vocês não têm nenhum dado real. Como sabem que a solução funciona?**
Não sabemos ainda, e a documentação não afirma isso. A massa sintética tem 34 situações planejadas com gabarito, e as 13 regras de qualidade marcaram todas as situações de erro sem marcar os controles negativos. Mas as regras foram escritas conhecendo os erros injetados: isso prova que a **mecânica** funciona, não o desempenho com dados reais. A prova de desempenho tem critérios de aceite nas próximas Sprints: precisão de 98% nos campos monetários de documentos reais e cobertura calibrada no backtest ([roadmap](roadmap.md#sprint-3-diagnóstico-benchmark-e-recomendações); [ingestão](ingestao-qualidade.md#9-resultados-na-massa-sintética)).

**2. A estimativa do último nível deixou o valor real de fora. Isso não invalida o método?**
Não sozinho. Uma faixa P10-P90 bem calibrada erra, por definição, uma vez em cada cinco; um caso isolado não prova nem refuta nada. Por isso testamos a calibração em 280 ensaios. O teste mostrou dois problemas, e os dois estão documentados: com a premissa genérica os erros se concentram acima do P90 (viés), e com a premissa calibrada a faixa ficou larga demais (95,8% de cobertura). O critério de aceite da Sprint 3 reprovaria os dois ([diagnóstico](diagnostico.md#5-estimativa-progressiva-e-perguntas-guiadas)).

**3. De onde vêm as premissas da estimativa, como km/L, preço do diesel e custo de manutenção?**
São hipóteses do grupo, listadas em [`data/parametros-simulacao.csv`](../data/parametros-simulacao.csv), e não números de mercado. Elas servem para demonstrar o procedimento. Em produção, devem ser substituídas por referências externas versionadas (como a série de preços da ANP) e calibradas com o histórico dos clientes ([referências](referencias.md#3-métodos-quantitativos)).

**4. Se o cliente enviar o mesmo arquivo duas vezes, o custo dobra?**
Não. Cada arquivo recebe um hash SHA-256 na recepção, e a regra R-DUP-ARQ bloqueia o reenvio. Na EMP-B fictícia, o reenvio injetado somaria R$ 110.539,04 (8,2% do custo) se não fosse detectado. Registros repetidos em arquivos diferentes caem na regra R-DUP-REG ([ingestão](ingestao-qualidade.md#5-duplicidades-e-reconciliação)).

**5. E documentos ruins, como foto de nota amassada?**
A extração devolve confiança por campo. Abaixo de 0,80, o registro vai para quarentena e para a fila de revisão humana, ao lado do recorte do documento; o valor em quarentena não entra nos totais até ser confirmado. A correção guarda o valor original ([ingestão](ingestao-qualidade.md#6-documentos-ilegíveis-e-erros-de-extração)).

## Método e economia

**6. Custo alto é desperdício? Como vocês evitam acusar um caminhão que simplesmente roda mais?**
Separando volume de eficiência. O custo de combustível é decomposto em atividade (km), intensidade (L/km) e preço (R$/L) pelo método LMDI. No exemplo, C-V01 custa mais porque roda mais e consome melhor que os pares; C-V07 piorou o consumo de 2,34 para 2,02 km/L. Cinco situações justificáveis do gabarito (como IPVA pago de uma vez, preventiva programada e evento extraordinário) não foram marcadas como problema ([benchmarks](benchmarks.md#4-decomposição-atividade-intensidade-e-preço)).

**7. Um ROI de 590% no cenário otimista da EMP-C não é exagerado?**
O cenário otimista inclui uma hipótese que depende de validação jurídica e contratual (lotação sem Vale-Pedágio) e por isso é rotulado como teto. O ROI já é calculado sobre o custo total, com custos recorrentes e o custo de operar o plano, e não só sobre a implantação. A decisão deve usar o conservador (R$ 21.464 por ano) ou o base (R$ 119.594). A análise de sensibilidade mostra o base caindo para R$ 53.915 se a captura for 20% menor e os custos dobrarem ([economia](economia-recomendacoes.md#3-cenários-escada-de-evidência)).

**8. Por que a EMP-B tem economia líquida negativa? Isso não mata o produto?**
Porque o custo de executar um programa de redução (R$ 12.000 por ano na hipótese) é maior do que as oportunidades encontradas. Mostrar isso é parte do valor: a calculadora não inventa economia. O próximo passo recomendado para a EMP-B é a ação isolada de maior valor e sem custo, indicar condutores no prazo para evitar multas NIC (R$ 2.033 por ano na frota fictícia), sem montar um programa ([economia](economia-recomendacoes.md#5-priorização-e-próximo-passo)).

**9. Como vocês evitam contar a mesma economia duas vezes?**
Alavancas sobre o mesmo custo são combinadas multiplicativamente: reduções de 6% e 4% sobre R$ 200.000 somam R$ 19.520, e não R$ 20.000. Além disso, preço e consumo são efeitos disjuntos da decomposição, alternativas excludentes não entram juntas no mesmo cenário, recuperação pontual não se soma à economia anual, e corrigir um erro de dado não conta como economia ([economia](economia-recomendacoes.md#4-dupla-contagem)).

**10. O índice de confiança de vocês é uma probabilidade?**
Não, e a documentação diz isso explicitamente. É uma medida ordinal com cinco dimensões (completude, atualidade, consistência, rastreabilidade e contexto), inspirada na ISO/IEC 25012. O selo usa a pior dimensão, não a média, porque uma média alta esconderia uma falha grave. A EMP-A fica com selo "Baixa" porque a atualidade dos dados (58,5) é a pior dimensão ([diagnóstico](diagnostico.md#6-índice-de-confiabilidade)).

**11. Por que não usar um modelo de IA para calcular tudo?**
Porque valores financeiros precisam ser reproduzíveis e auditáveis, e modelos de linguagem erram aritmética. A IA entra onde ajuda: leitura de documentos, classificação de despesas e explicação em linguagem natural. Todo número de um texto gerado é conferido contra o cálculo determinístico antes de aparecer. Nenhum modelo foi treinado nesta Sprint ([estratégia de IA](estrategia-ia.md#3-verificação-numérica-de-textos-gerados)).

## Negócio e Sem Parar Empresas

**12. A ferramenta não vira só um catálogo para empurrar produtos da Sem Parar Empresas?**
A recomendação é sempre uma ação do gestor, e não um produto. A solução do portfólio aparece só quando ajuda a executar aquela ação, com texto que informa que é solução do portfólio e que não há garantia de economia. Nenhum percentual de economia é atribuído aos produtos. O catálogo de associações ainda precisa ser revisado pela Sem Parar Empresas ([economia](economia-recomendacoes.md#7-relação-com-o-portfólio-sem-parar-empresas)).

**13. A US-SP-06 pede para tratar todos os clientes como leads. Vocês não atenderam?**
Atendemos com restrição legal, e registramos isso como decisão. O contato de serviço é sempre registrado. O uso comercial depende de uma autorização separada, opcional e revogável; sem ela, o painel da Sem Parar Empresas mostra só contagens agregadas. A interpretação irrestrita violaria os princípios de finalidade e necessidade da LGPD ([segurança e LGPD](seguranca-lgpd.md#4-finalidades-comerciais-leads-e-benchmarks); [User Stories](user-stories.md#us-sp-06)).

**14. Qual é o diferencial em relação a uma planilha ou a um sistema de telemetria?**
Três coisas que uma planilha não faz sozinha: consolidar fontes heterogêneas com origem e status de cada valor; dar uma estimativa útil no primeiro uso, como faixa com confiança, e dizer qual informação melhora mais a estimativa; e transformar achados em economia líquida por cenário, sem confundir volume com desperdício. Telemetria mede o veículo, mas não consolida custo, multa, tributo e pedágio ([solução](solucao.md#6-diferenciais-avaliados)).

**15. Como vocês comparam frotas diferentes? Existe benchmark de mercado?**
A comparação segue uma hierarquia: primeiro a própria história, depois pares da mesma frota, depois grupos entre clientes (só com tamanho mínimo de grupo, para não identificar ninguém) e, por último, referências externas como a ANP. Há regras explícitas de quando **não** comparar, como veículo locado com manutenção inclusa contra veículo próprio ([benchmarks](benchmarks.md#3-quando-não-comparar)).

## Arquitetura, segurança e execução

**16. Como um cliente fica impedido de ver os dados de outro?**
Isolamento no banco com segurança em nível de linha no PostgreSQL, identificador do cliente em toda tabela de negócio e teste automatizado de vazamento entre clientes como critério de aceite da Sprint 2. A lista de verificação de segurança é o OWASP ASVS nível 2 ([segurança](seguranca-lgpd.md#2-requisitos-de-segurança); [arquitetura](arquitetura.md)).

**17. São 14 User Stories "Must". Dá para entregar em 8 meses?**
É o principal risco de escopo (RSK-08). A mitigação é a ordem de dependência do roadmap e a regra de que nada *Could* começa antes dos *Must*. O calendário de quatro Sprints é hipótese até a confirmação do calendário oficial ([roadmap](roadmap.md#5-riscos-do-projeto)).

**18. Como vocês vão medir a economia que de fato aconteceu?**
Pela lógica de medição e verificação do IPMVP: compara-se o gasto real com o que se teria gastado sem a ação, numa linha de base ajustada às condições do período (quilometragem, preço). A economia realizada só aparece depois de medida ([diagnóstico](diagnostico.md#2-da-observação-à-economia-realizada)).

**19. Este trabalho foi feito por IA?**
Uma ferramenta de IA generativa produziu a primeira versão da documentação, dos dados e dos scripts, e isso está declarado em [uso de IA](uso-de-ia.md), com o histórico de commits mostrando a autoria da ferramenta. As decisões de escopo foram do grupo, e a responsabilidade pelo conteúdo é do grupo, que precisa revisar e dominar cada documento antes da entrega.

**20. As leis citadas estão corretas e atualizadas?**
Foram conferidas por mecanismo de busca, porque os sites oficiais estavam bloqueados no ambiente de trabalho, e cada referência informa esse nível de verificação. Elas orientam requisitos e não constituem parecer jurídico; a validação por profissional habilitado é condição antes do piloto (RSK-07) ([referências](referencias.md#2-legislação-e-regulação)).

## Resumo

| Pergunta | Respondida pelos documentos | Efeito no projeto |
|---|---|---|
| 1, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 | Sim | Nenhuma mudança necessária |
| 2 | Parcialmente | A cobertura de 95,8% (faixa larga demais) não estava comentada; adicionado ao [diagnóstico](diagnostico.md#5-estimativa-progressiva-e-perguntas-guiadas) |
| 3 | Sim | Reforçado em [referências](referencias.md#3-métodos-quantitativos) que as premissas não têm fonte externa |
| 7 | Parcialmente | O fator de captura "base" da hipótese OP-C4 parecia contradizer a escada de evidência; explicação adicionada em [economia](economia-recomendacoes.md#3-cenários-escada-de-evidência) |
| 8 | Sim | O roteiro do vídeo dizia "quase zero" para um resultado negativo; texto corrigido |

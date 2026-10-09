# Narração do vídeo da Sprint 1

Arquivo gerado por [`src/gerar_video.py`](../../src/gerar_video.py) a partir do [roteiro](roteiro.md). Para mudar o texto, edite o roteiro e gere de novo; os tempos se ajustam.

**Duração total: 4:44.** A fala começa em 0:03, depois da contagem regressiva, no ritmo de 140 palavras por minuto. Cada linha mostra o instante em que a frase começa na animação.

| Início | Frase |
|---|---|
| **0:03** | **Cena 1: Abertura** |
| 0:03 | Olá. |
| 0:04 | Este é o Frota Pulse, nossa proposta para a Calculadora de Redução de Custos de Frota, no Enterprise Challenge da FIAP com a Sem Parar Empresas. |
| 0:15 | Nesta primeira Sprint, o objetivo foi planejar: o que construir, com quais dados e como provar que funciona. |
| **0:24** | **Cena 2: O problema** |
| 0:24 | O briefing resume bem o problema: o gestor sabe quanto gastou, mas não onde está perdendo. |
| 0:31 | Combustível, manutenção, pedágio, multas e impostos ficam em sistemas separados. |
| 0:36 | Nós dividimos isso em cinco problemas. |
| 0:38 | Os dados chegam fragmentados. |
| 0:40 | Custo absoluto não mostra eficiência. |
| 0:42 | Custo alto nem sempre é desperdício. |
| 0:45 | Diagnóstico sem ação não resolve. |
| 0:47 | E quase nunca o gestor tem todos os documentos no primeiro uso. |
| **0:53** | **Cena 3: User Stories** |
| 0:54 | Trabalhamos com as vinte User Stories oficiais, do gestor de frota, do CFO e da Sem Parar Empresas. |
| 1:02 | Todas estão numa matriz de rastreabilidade, com funcionalidade, critério de aceitação e Sprint prevista. |
| 1:08 | Quatro delas definem o produto: ter sempre uma estimativa, mesmo com poucos dados; receber perguntas sobre o que informar; ver a economia em reais; e, para a Sem Parar Empresas, gerar oportunidades comerciais. |
| 1:22 | Esta última nós atendemos com regra de LGPD: contato comercial só com base legal e preferência registrada. |
| **1:31** | **Cena 4: Visão do produto** |
| 1:31 | O Frota Pulse tem cinco capacidades: entender os dados, diagnosticar, comparar, otimizar e acompanhar. |
| 1:37 | O diferencial é dizer quanto se pode confiar em cada número. |
| 1:42 | Toda estimativa aparece como faixa, com a parte que vem de documento e um selo de confiança. |
| **1:51** | **Cena 5: Dados** |
| 1:51 | No modelo de dados, a despesa é o centro, e nenhum valor existe sem a origem: arquivo, linha e status, que pode ser observado, corrigido, imputado, estimado ou não disponível. |
| 2:04 | Para testar tudo, geramos dados sintéticos de três frotas fictícias, com trinta e quatro situações planejadas, como arquivo enviado duas vezes, odômetro errado e cobrança duplicada. |
| 2:15 | As regras de qualidade detectaram todos os erros injetados. |
| 2:19 | Só que nós escrevemos as regras sabendo dos erros; isso prova a mecânica, não o desempenho com dados reais. |
| **2:29** | **Cena 6: Estimativa progressiva** |
| 2:29 | A estimativa é progressiva. |
| 2:31 | Só com a composição da frota, a faixa de seis meses da empresa pequena vai de cento e dezesseis a cento e cinquenta e cinco mil reais. |
| 2:43 | Com duas respostas e alguns extratos, ela estreita. |
| 2:46 | E o sistema sempre sugere a próxima pergunta, a que mais reduz a incerteza por esforço. |
| 2:53 | No último nível, o valor real caiu fora da faixa. |
| 2:57 | Mostramos isso de propósito: uma faixa honesta erra às vezes, e por isso testamos a calibração em centenas de ensaios. |
| **3:07** | **Cena 7: Custo alto não é desperdício** |
| 3:08 | Para não confundir volume com ineficiência, decompomos o custo de combustível em quilômetros, consumo e preço. |
| 3:15 | Um caminhão que roda quase cinquenta por cento a mais que os parecidos custa mais, mas gasta menos diesel por quilômetro: é eficiente. |
| 3:25 | Outro piorou o consumo, e um método de soma acumulada detectou a queda em um a dois meses, sem alarme falso entre quarenta veículos. |
| **3:36** | **Cena 8: Economia em três cenários** |
| 3:37 | Cada achado vira ação, com economia em três cenários, que diferem pelo nível de evidência. |
| 3:44 | Na frota maior, o cenário-base é de cerca de cento e vinte mil reais líquidos por ano, já descontando o custo de executar o plano. |
| 3:54 | Na frota média, o cenário-base fica negativo: executar o plano custa mais do que ele economiza. |
| 4:01 | Isso também é resposta: a calculadora não precisa inventar economia. |
| **4:07** | **Cena 9: Arquitetura** |
| 4:07 | A arquitetura é um monólito modular em Python, com FastAPI, PostgreSQL com isolamento por cliente e um processo separado para ler documentos. |
| 4:17 | Os cálculos financeiros são determinísticos e versionados; a IA ajuda a ler e a explicar, mas não calcula. |
| **4:26** | **Cena 10: Próximos passos** |
| 4:27 | Nas próximas Sprints, vamos construir a ingestão e a primeira estimativa, depois o diagnóstico com benchmarks e recomendações, e por fim testar com gestores reais. |
| 4:37 | Toda a documentação está no repositório. |
| 4:40 | Obrigado. |

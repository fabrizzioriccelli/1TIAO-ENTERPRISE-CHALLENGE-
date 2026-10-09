# Vídeo da Sprint 1: roteiro, storyboard e checklist

> O vídeo **ainda não foi gravado**. Este documento e os [slides de apoio](slides-apoio.pdf) (gerados por [`src/gerar_slides.py`](../../src/gerar_slides.py)) preparam a gravação. Duração máxima: **5 minutos**. O roteiro tem cerca de 600 palavras, o que dá em torno de 4 minutos e 20 segundos em ritmo de apresentação (130 a 150 palavras por minuto) e deixa margem para pausas e troca de slides.

## 1. Distribuição do tempo

| Bloco | Tempo | Slide | Conteúdo obrigatório coberto |
|---|---|---|---|
| 1. Abertura | 0:00 a 0:20 | 1 | Projeto e contexto |
| 2. Problema | 0:20 a 0:50 | 2 | Problema e contexto |
| 3. User Stories | 0:50 a 1:25 | 3 | User Stories escolhidas |
| 4. Visão do produto | 1:25 a 1:55 | 4 | Visão do produto |
| 5. Dados | 1:55 a 2:30 | 5 | Estrutura dos dados |
| 6. Metodologia | 2:30 a 3:30 | 6 e 7 | Metodologia proposta |
| 7. Economia | 3:30 a 3:55 | 8 | Metodologia (economia e recomendação) |
| 8. Arquitetura | 3:55 a 4:20 | 9 | Arquitetura |
| 9. Próximas etapas | 4:20 a 4:40 | 10 | Planejamento |

## 2. Roteiro de narração

Escrito para ser **falado**, não lido. Antes de gravar, quem vai narrar deve ler o roteiro em voz alta e ajustar as palavras que não soem naturais na sua fala. Os números citados estão no [anexo de exemplos](../anexos/exemplos-calculados.md).

**[Slide 1 · Abertura]**
Olá. Este é o Frota Pulse, nossa proposta para a Calculadora de Redução de Custos de Frota, no Enterprise Challenge da FIAP com a Sem Parar Empresas. Nesta primeira Sprint, o objetivo foi planejar: o que construir, com quais dados e como provar que funciona.

**[Slide 2 · Problema]**
O briefing resume bem o problema: o gestor sabe quanto gastou, mas não onde está perdendo. Combustível, manutenção, pedágio, multas e impostos ficam em sistemas separados. Nós dividimos isso em cinco problemas. Os dados chegam fragmentados. Custo absoluto não mostra eficiência. Custo alto nem sempre é desperdício. Diagnóstico sem ação não resolve. E quase nunca o gestor tem todos os documentos no primeiro uso.

**[Slide 3 · User Stories]**
Trabalhamos com as vinte User Stories oficiais, do gestor de frota, do CFO e da Sem Parar Empresas. Todas estão numa matriz de rastreabilidade, com funcionalidade, critério de aceitação e Sprint prevista. Quatro delas definem o produto: ter sempre uma estimativa, mesmo com poucos dados; receber perguntas sobre o que informar; ver a economia em reais; e, para a Sem Parar Empresas, gerar oportunidades comerciais. Esta última nós atendemos com regra de LGPD: contato comercial só com base legal e preferência registrada.

**[Slide 4 · Visão do produto]**
O Frota Pulse tem cinco capacidades: entender os dados, diagnosticar, comparar, otimizar e acompanhar. O diferencial é dizer quanto se pode confiar em cada número. Toda estimativa aparece como faixa, com a parte que vem de documento e um selo de confiança.

**[Slide 5 · Dados]**
No modelo de dados, a despesa é o centro, e nenhum valor existe sem a origem: arquivo, linha e status, que pode ser observado, corrigido, imputado, estimado ou não disponível. Para testar tudo, geramos dados sintéticos de três frotas fictícias, com trinta e quatro situações planejadas, como arquivo enviado duas vezes, odômetro errado e cobrança duplicada. As regras de qualidade detectaram todos os erros injetados. Só que nós escrevemos as regras sabendo dos erros; isso prova a mecânica, não o desempenho com dados reais.

**[Slide 6 · Metodologia: estimativa]**
A estimativa é progressiva. Só com a composição da frota, a faixa de seis meses da empresa pequena vai de cento e dezesseis a cento e cinquenta e cinco mil reais. Com duas respostas e alguns extratos, ela estreita. E o sistema sempre sugere a próxima pergunta, a que mais reduz a incerteza por esforço. No último nível, o valor real caiu fora da faixa. Mostramos isso de propósito: uma faixa honesta erra às vezes, e por isso testamos a calibração em centenas de ensaios.

**[Slide 7 · Metodologia: custo alto não é desperdício]**
Para não confundir volume com ineficiência, decompomos o custo de combustível em quilômetros, consumo e preço. Um caminhão que roda vinte e cinco por cento a mais custa mais, mas é eficiente. Outro piorou o consumo, e um método de soma acumulada detectou a queda em um a dois meses, sem alarme falso entre quarenta veículos.

**[Slide 8 · Economia]**
Cada achado vira ação, com economia em três cenários, que diferem pelo nível de evidência. Na frota maior, o cenário-base é de cerca de cento e vinte mil reais líquidos por ano, já descontando o custo de executar o plano. Na frota média, o cenário-base fica negativo: executar o plano custa mais do que ele economiza. Isso também é resposta: a calculadora não precisa inventar economia.

**[Slide 9 · Arquitetura]**
A arquitetura é um monólito modular em Python, com FastAPI, PostgreSQL com isolamento por cliente e um processo separado para ler documentos. Os cálculos financeiros são determinísticos e versionados; a IA ajuda a ler e a explicar, mas não calcula.

**[Slide 10 · Próximos passos]**
Nas próximas Sprints, vamos construir a ingestão e a primeira estimativa, depois o diagnóstico com benchmarks e recomendações, e por fim testar com gestores reais. Toda a documentação está no repositório. Obrigado.

## 3. Storyboard

| Slide | Visual | Movimento na tela | Pontos essenciais |
|---|---|---|---|
| 1 | Capa: marca, frase e as cinco capacidades | Estático | Nome do projeto, FIAP e Sem Parar Empresas, Sprint 1 |
| 2 | Citação do briefing e lista P1 a P5 | Itens aparecem um a um, opcional | O problema em frase oficial |
| 3 | Três colunas com contagem de User Stories por visão e as quatro em destaque | Estático | 20 oficiais, matriz e MoSCoW, LGPD em US-SP-06 |
| 4 | Cinco capacidades e os quatro princípios do briefing | Estático | Faixa, parcela observada e selo |
| 5 | Diagrama simplificado (despesa no centro) e quadro das três frotas | Estático | Origem e status; 34 cenários; limitação do teste |
| 6 | Gráfico [estimativa progressiva](../../assets/graficos/estimativa-progressiva.svg) | Destacar o N3 fora da faixa | Faixa que estreita; próxima pergunta; honestidade |
| 7 | Gráfico [LMDI](../../assets/graficos/decomposicao-lmdi.svg) | Destacar C-V01 e C-V07 | Volume não é desperdício; detecção em 1 a 2 meses |
| 8 | Gráfico [cenários](../../assets/graficos/cenarios-economia.svg) | Estático | Escada de evidência; resultado líquido; EMP-B |
| 9 | [Diagrama de arquitetura](../../assets/diagramas/arquitetura-geral.svg) | Estático | Monólito modular; IA não calcula |
| 10 | Linha do tempo S1 a S4 e endereço do repositório | Estático | Próximos passos |

## 4. Recomendações para a apresentação

- **Um narrador.** Um único integrante grava a narração do roteiro inteiro. Ele precisa dominar todo o conteúdo, e os demais revisam o roteiro e os slides antes da gravação; a banca pode perguntar qualquer número a qualquer integrante.
- **Ensaiar com cronômetro** duas vezes. Se passar de 4:45, cortar exemplos, não pressa na fala.
- **Falar com as próprias palavras.** O roteiro é guia; leitura monótona prejudica a avaliação.
- **Mostrar, não descrever:** quando citar um número, ele deve estar visível no slide.
- **Não chamar números sintéticos de reais.** Dizer "na frota fictícia".
- Evitar promessas: "pode reduzir", não "vai reduzir".

## 5. Checklist de gravação e publicação

**Antes de gravar**
- [x] Integrantes preenchidos no README e no slide 1
- [ ] Slides revisados pelo grupo; números conferidos com o anexo
- [ ] Ensaio cronometrado abaixo de 4:45

**Gravação**
- [ ] Resolução de 1920 × 1080; slides em tela cheia
- [ ] Narração feita por um integrante do grupo: o enunciado exige **narração humana**, então não usar voz sintética
- [ ] Microfone testado; ambiente sem eco nem ruído
- [ ] Câmera opcional; se houver, no canto, sem cobrir conteúdo
- [ ] Duração final até 5:00

**Publicação**
- [ ] YouTube com visibilidade **não listado** (não "privado", que impede a banca de assistir)
- [ ] Título sugerido: "Frota Pulse — Enterprise Challenge FIAP e Sem Parar Empresas — Sprint 1"
- [ ] Descrição com o link do repositório e a observação "dados sintéticos; projeto acadêmico"
- [ ] Link testado em janela anônima, sem login
- [ ] Link inserido no README (seção "Links do Projeto") e no arquivo [`ENTREGA_SPRINT1_LINKS.txt`](../../ENTREGA_SPRINT1_LINKS.txt)
- [ ] Commit com a mensagem "Adicionar link do vídeo da Sprint 1", **antes da data limite**: depois dela o repositório não pode ser alterado

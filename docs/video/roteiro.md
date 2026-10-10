# Vídeo da Sprint 1: roteiro, animação e narração

> **Vídeo publicado:** https://youtu.be/MD6aKeIHl-Y (não listado), com narração gravada por um integrante sobre a animação abaixo.
>
> **Como foi feito.** A animação foi gerada sem voz. O enunciado exige narração humana, então um integrante grava a voz por cima da animação. Duração: **4:42**, dentro do limite de 5 minutos. A animação é gerada por [`src/gerar_video.py`](../../src/gerar_video.py) e gravada por [`src/gravar_video.js`](../../src/gravar_video.js) em duas versões:
>
> - **Versão final** (`frota-pulse-sprint1-video.mp4`): sem texto na tela; é a que vai para o YouTube depois de receber a voz.
> - **Versão guia** (`frota-pulse-sprint1-guia-narracao.mp4`): igual, mas com a frase a ser falada no rodapé e uma contagem regressiva no início; serve para o narrador acompanhar o ritmo.
>
> O texto com o tempo de cada frase está em [narracao.md](narracao.md), e as legendas para o YouTube em [legendas.srt](legendas.srt). Os [slides de apoio](slides-apoio.pdf) continuam disponíveis como alternativa.

## 1. Cenas e tempos

| Cena | Início | Fim | Conteúdo exigido pelo enunciado |
|---|---|---|---|
| 1. Abertura | 0:03 | 0:24 | Projeto e contexto |
| 2. O problema | 0:24 | 0:53 | Entendimento do problema |
| 3. User Stories | 0:53 | 1:31 | User Stories escolhidas |
| 4. Visão do produto | 1:31 | 1:51 | Solução proposta |
| 5. Dados | 1:51 | 2:29 | Dados que serão utilizados |
| 6. Estimativa progressiva | 2:29 | 3:07 | Solução: dados incompletos e orientação ao usuário |
| 7. Custo alto não é desperdício | 3:07 | 3:36 | Solução: diagnóstico |
| 8. Economia em três cenários | 3:36 | 4:07 | Solução: recomendações e economia |
| 9. Arquitetura | 4:07 | 4:26 | Arquitetura inicial |
| 10. Próximos passos | 4:26 | 4:42 | Planejamento |

Os primeiros 3 segundos mostram só a marca (na versão guia, a contagem regressiva). A fala começa em 0:03.

## 2. Roteiro de narração

Escrito para ser **falado**, não lido. Este texto é a fonte do vídeo: o tempo de cada cena sai da contagem de palavras. Se o narrador mudar alguma frase, edite aqui e rode `python src/gerar_video.py` para recalcular os tempos. Os números citados estão no [anexo de exemplos](../anexos/exemplos-calculados.md).

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
Para não confundir volume com ineficiência, decompomos o custo de combustível em quilômetros, consumo e preço. Um caminhão que roda quase cinquenta por cento a mais que os parecidos custa mais, mas gasta menos diesel por quilômetro: é eficiente. Outro piorou o consumo, e um método de soma acumulada detectou a queda em um a dois meses, sem alarme falso entre quarenta veículos.

**[Slide 8 · Economia]**
Cada achado vira ação, com economia em três cenários, que diferem pelo nível de evidência. Na frota maior, o cenário-base é de cerca de cento e vinte mil reais líquidos por ano, já descontando o custo de executar o plano. Na frota média, o cenário-base fica negativo: executar o plano custa mais do que ele economiza. Isso também é resposta: a calculadora não precisa inventar economia.

**[Slide 9 · Arquitetura]**
A arquitetura é um monólito modular em Python, com FastAPI, PostgreSQL com isolamento por cliente e um processo separado para ler documentos. Os cálculos financeiros são determinísticos e versionados; a IA ajuda a ler e a explicar, mas não calcula.

**[Slide 10 · Próximos passos]**
Nas próximas Sprints, vamos construir a ingestão e a primeira estimativa, depois o diagnóstico com benchmarks e recomendações, e por fim testar com gestores reais. Toda a documentação está no repositório. Obrigado.

## 3. O que aparece em cada cena

| Cena | Animação |
|---|---|
| 1 | Marca, título e subtítulo entram; três etiquetas (o que construir, com quais dados, como provar) aparecem com a fala; nomes dos integrantes; linha de pulso desenhada ao fundo |
| 2 | A frase do briefing é digitada letra por letra; aparecem cinco exemplos de documentos e, um a um, os cartões P1 a P5, cada um no momento em que é falado |
| 3 | Contadores de User Stories por perfil (10, 4 e 6); matriz de 20 blocos coloridos por prioridade; as quatro User Stories principais entram uma a uma; selo de LGPD |
| 4 | As cinco capacidades; a pergunta "Quanto se pode confiar em cada número?"; uma faixa de R$ 128 mil a R$ 141 mil com 76% vindo de documentos e o selo de confiança |
| 5 | Modelo de dados com a despesa no centro e as ligações sendo desenhadas; status do valor; três frotas fictícias com contadores; 34 situações planejadas; resultado das regras e o aviso de limitação |
| 6 | Gráfico das faixas N0 a N3 crescendo em relação ao valor real; a próxima pergunta sugerida; o N3 marcado como "fora da faixa"; 280 ensaios de calibração |
| 7 | A fórmula custo = km × litros por km × preço; barras da decomposição do C-V01; curva da soma acumulada do C-V07 sendo desenhada até o alarme de fev/26 |
| 8 | Achado → ação → economia; colunas dos três cenários crescendo; destaque do cenário-base da EMP-C e do resultado negativo da EMP-B |
| 9 | As sete etapas do fluxo pedido no enunciado aparecem em sequência; tecnologias; separação entre cálculo determinístico e IA |
| 10 | Linha do tempo das Sprints; endereço do repositório; "Obrigado." e nomes do grupo |

Uma barra de progresso no rodapé mostra o andamento e a divisão entre as cenas.

## 4. Como gravar a narração

Só uma pessoa narra o vídeo inteiro. Ela não precisa mexer em slides nem em tela: só falar.

1. **Ensaiar.** Assistir à versão guia uma vez lendo junto, em voz alta. O ritmo é de cerca de 140 palavras por minuto, calmo. Ajustar palavras difíceis no texto da seção 2 (e regenerar o vídeo, se mudar muito).
2. **Gravar a voz assistindo à versão guia.** Opções:
   - **CapCut ou Clipchamp (mais simples):** importar a versão guia, usar a função de gravar narração com o vídeo tocando, depois trocar a faixa de vídeo pela versão final, que tem exatamente a mesma duração. A voz fica sincronizada.
   - **Celular:** tocar a versão guia no computador e gravar a voz no celular, começando no mesmo instante. Depois juntar áudio e versão final no editor, alinhando o início da fala com 0:03.
3. **Conferir o sincronismo** em três pontos: os cartões P1 a P5 (cena 2), o "fora da faixa" (cena 6) e o "Obrigado." (cena 10). Se a voz atrasar ou adiantar, cortar ou estender pausas no editor.
4. **Exportar** em 1080p, MP4.

**Dicas:** falar perto do microfone, em ambiente silencioso; manter a mesma distância durante toda a gravação; se errar uma frase, fazer uma pausa e repetir a frase inteira, e cortar o erro depois.

## 5. Checklist de gravação e publicação

**Antes de gravar**
- [ ] Narrador definido e roteiro ensaiado com a versão guia
- [ ] Números conferidos com o [anexo de exemplos](../anexos/exemplos-calculados.md)

**Gravação**
- [ ] Narração feita por um integrante do grupo: o enunciado exige **narração humana**, então não usar voz sintética
- [ ] Microfone testado; ambiente sem eco nem ruído
- [ ] Voz montada sobre a **versão final** (sem texto na tela)
- [ ] Duração final até 5:00

**Publicação**
- [ ] YouTube com visibilidade **não listado** (não "privado", que impede a banca de assistir)
- [ ] Título sugerido: "Frota Pulse — Enterprise Challenge FIAP e Sem Parar Empresas — Sprint 1"
- [ ] Descrição com o link do repositório e a observação "dados simulados; projeto acadêmico"
- [ ] Opcional: enviar [legendas.srt](legendas.srt) como legenda, revisando se a fala mudou
- [ ] Link testado em janela anônima, sem login
- [ ] Link inserido no README (seção "Links do Projeto") e no arquivo [`ENTREGA_SPRINT1_LINKS.txt`](../../ENTREGA_SPRINT1_LINKS.txt)
- [ ] Commit com a mensagem "Adicionar link do vídeo da Sprint 1", **antes da data limite**: depois dela o repositório não pode ser alterado

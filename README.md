# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="assets/logo-fiap.png" 
       alt="FIAP - Faculdade de Informática e Administração Paulista" 
       width="40%">
</a>
</p>

<br>

# Frota Pulse: Calculadora de Redução de Custos de Frota

Enterprise Challenge FIAP e Sem Parar Empresas · Sprint 1 · Turma 1TIAO

## Nome do grupo

Grupo sem nome definido · Turma 1TIAO

## 👨‍🎓 Integrantes: 
- <a href="https://github.com/brunacollavite">Bruna Collavite</a> - RM 576285
- <a href="https://github.com/Guntooo">Fabio Guntovitch</a> - RM 575582
- <a href="https://github.com/fabrizzioriccelli">Fabrizzio Riccelli</a> - RM 576083
- <a href="https://github.com/GabrielTamaisFischer">Gabriel Tamais</a> - RM 574503
- Natasha Zonta - RM 574230

## 👩‍🏫 Professores:

### Tutor(a)
- Sabrina Otoni
  
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

## 📜 Descrição

![Capa conceitual do Frota Pulse](assets/capa-frota-pulse.png)

**O problema.** Nas palavras do briefing da Sem Parar Empresas: "O gestor sabe quanto gastou — mas não onde está perdendo." Combustível, manutenção, pedágio, multas e impostos ficam em sistemas e documentos separados, e o custo real da frota nunca aparece consolidado. O desafio pede uma calculadora que transforme esses dados em diagnóstico, recomendações e economia estimada, atendendo a 20 User Stories oficiais do gestor de frota, do CFO e da própria Sem Parar Empresas.

**A proposta.** O Frota Pulse (nome provisório, sem relação com marcas oficiais) organiza o produto em cinco capacidades: **entender** documentos em qualquer formato, **diagnosticar** com indicadores normalizados, **comparar** só quando há equivalência, **otimizar** com ações e economia em reais por cenário, e **acompanhar** a economia realizada mês a mês. O diferencial é dizer quanto se pode confiar em cada número: toda estimativa aparece como faixa provável, com a parcela que vem de documento e um selo de confiança, e o sistema sugere a próxima informação que mais reduz a incerteza.

**O que esta Sprint entrega.** A Sprint 1 é de especificação. Não há aplicação implementada; há documentação, dados sintéticos e scripts que demonstram e testam os métodos propostos.

| Tema | Documento |
|---|---|
| Problema, objetivos, escopo e premissas | [docs/problema.md](docs/problema.md) |
| Personas hipotéticas e roteiro de entrevista | [docs/personas.md](docs/personas.md) |
| Matriz de rastreabilidade das 20 User Stories (MoSCoW) | [docs/user-stories.md](docs/user-stories.md) |
| Visão do produto, funcionalidades e diferenciais | [docs/solucao.md](docs/solucao.md) |
| Modelo de dados, competência e massa sintética | [docs/modelagem-dados.md](docs/modelagem-dados.md) e [data/dicionario-dados.csv](data/dicionario-dados.csv) |
| Ingestão e qualidade dos dados | [docs/ingestao-qualidade.md](docs/ingestao-qualidade.md) |
| Indicadores, estimativa progressiva e confiabilidade | [docs/diagnostico.md](docs/diagnostico.md) |
| Benchmarks e decomposição do custo | [docs/benchmarks.md](docs/benchmarks.md) |
| Economia, cenários, priorização e recomendações | [docs/economia-recomendacoes.md](docs/economia-recomendacoes.md) |
| Estratégia de IA por componente | [docs/estrategia-ia.md](docs/estrategia-ia.md) |
| Arquitetura, decisões e diagramas | [docs/arquitetura.md](docs/arquitetura.md) |
| Segurança e LGPD | [docs/seguranca-lgpd.md](docs/seguranca-lgpd.md) |
| UX, identidade visual e wireframes conceituais | [docs/ux-identidade-visual.md](docs/ux-identidade-visual.md) |
| Roadmap, papéis, Kanban e riscos | [docs/roadmap.md](docs/roadmap.md) |
| Exemplos calculados sobre a massa sintética | [docs/anexos/exemplos-calculados.md](docs/anexos/exemplos-calculados.md) |
| Roteiro, storyboard e slides do vídeo | [docs/video/roteiro.md](docs/video/roteiro.md) |
| Verificações, auditoria e matriz de conclusão | [docs/validacao.md](docs/validacao.md) |
| Perguntas difíceis da banca, respondidas | [docs/teste-adversarial.md](docs/teste-adversarial.md) |
| Referências e nível de verificação | [docs/referencias.md](docs/referencias.md) |
| Declaração de uso de IA | [docs/uso-de-ia.md](docs/uso-de-ia.md) |

**Alguns resultados sobre os dados sintéticos** (três frotas fictícias, 34 situações planejadas com gabarito):

- As 13 regras de qualidade marcaram todos os erros injetados e nenhum dos controles negativos. As regras foram escritas conhecendo os erros, então isso prova a mecânica, não o desempenho com dados reais.
- A estimativa da frota pequena começa em uma faixa de R$ 116 mil a R$ 155 mil só com a composição da frota e estreita a cada informação. No último nível, o valor real ficou fora da faixa; o caso é mostrado de propósito e a calibração foi testada em 280 ensaios.
- Na frota maior, o cenário-base indica cerca de R$ 120 mil por ano de economia líquida, já descontado o custo de executar o plano. Na frota média, o cenário-base fica negativo, e a calculadora diz isso em vez de inventar economia.

## 📁 Estrutura de pastas 

Abaixo encontra-se a descrição da organização da raiz do projeto e a finalidade de cada diretório e arquivo:

* **`assets/`** Capa, logo da FIAP do template, diagramas (`diagramas/`, SVG gerado do Mermaid), gráficos (`graficos/`), wireframes conceituais (`wireframes/`) e as fontes HTML e CSS editáveis (`fontes/`).

* **`data/`** Dicionário de dados (`dicionario-dados.csv`), premissas da simulação (`parametros-simulacao.csv`), massa sintética com gabarito (`sintetico/`) e resultados calculados (`resultados/`). **Nenhum dado real.**

* **`docs/`** Documentação técnica e de negócio da Sprint 1, anexos (`anexos/`) e materiais do vídeo (`video/`).

* **`notebooks/`** Reservada para análises exploratórias a partir da Sprint 2. Vazia nesta entrega.

* **`src/`** Scripts que geram a massa sintética, calculam os exemplos, desenham gráficos, wireframes e slides e validam a entrega. **Não é a aplicação**, que será construída a partir da Sprint 2.

* **`ENTREGA_SPRINT1_LINKS.txt`** Links do repositório e do vídeo para a entrega no portal.

* **`README.md`** Este arquivo. Funciona como o guia principal de introdução, configuração e contextualização do projeto.

## 📎 Links e Observações

### 🔗 Links do Projeto

* **Repositório (privado)**: https://github.com/fabrizzioriccelli/1TIAO-ENTERPRISE-CHALLENGE- - Documentação, dados sintéticos e scripts da Sprint 1.
* **Vídeo de entrega no YouTube**: **[Pendência: vídeo ainda não gravado nem publicado; inserir o link "não listado" após a publicação]** - Apresentação de até 5 minutos. Roteiro em [docs/video/roteiro.md](docs/video/roteiro.md).

### 🧠 Decisões Técnicas

> - **Monólito modular em Python (FastAPI) com PostgreSQL** e isolamento por cliente com segurança em nível de linha. Um processo separado lê documentos. Evita a complexidade de microsserviços em um produto de 8 meses com equipe pequena ([arquitetura](docs/arquitetura.md)).
> - **Cálculos financeiros determinísticos e versionados.** A IA lê documentos, classifica e explica, mas não calcula valores; todo número de um texto gerado é conferido contra o cálculo ([estratégia de IA](docs/estrategia-ia.md)).
> - **Nenhum valor sem origem.** Cada valor guarda arquivo, linha e status (observado, corrigido, imputado, estimado ou não disponível) ([modelagem](docs/modelagem-dados.md)).
> - **Estimativa como faixa, nunca como número único**, com perguntas guiadas pelo valor da informação e calibração por backtest ([diagnóstico](docs/diagnostico.md)).
> - **Custo alto não é desperdício.** O custo de combustível é decomposto em atividade, consumo e preço (LMDI), e quedas de rendimento são detectadas com CUSUM ([benchmarks](docs/benchmarks.md)).
> - **Economia líquida em três cenários** que diferem pelo nível de evidência, sem dupla contagem e sem percentuais atribuídos à Sem Parar Empresas ([economia](docs/economia-recomendacoes.md)).
> - **Uso comercial de dados só com base legal e preferência registrada** (LGPD), inclusive na User Story que pede tratar clientes como leads ([segurança e LGPD](docs/seguranca-lgpd.md)).
> - **Dados sintéticos com gabarito** para testar regras e métodos antes de ter dados reais, com as limitações declaradas.

### 📢 Observações Gerais

*Indique obrigatoriamente no campo abaixo a decisão da equipe quanto à participação no festival FIAP NEXT:*

* **Participação na Competição:** [ ] Sim, aceitamos participar / [ ] Não vamos participar. **[Pendência: decisão da equipe]**
* *Outras observações gerais (opcional):* projeto acadêmico. "Sem Parar Empresas", "Corpay" e os nomes de produtos citados pertencem aos seus titulares; o Frota Pulse não é produto oficial e não usa seus logotipos. A produção contou com apoio de IA generativa, declarado em [docs/uso-de-ia.md](docs/uso-de-ia.md). Itens pendentes de ação do grupo estão na [matriz de conclusão](docs/validacao.md#5-matriz-de-critérios-de-conclusão).

## 🔧 Como executar o código

**Pré-requisitos.** Python 3.11 ou mais recente e as bibliotecas de [`requirements.txt`](requirements.txt) (testado com Python 3.13, pandas 3.0 e NumPy 2.5). Opcionais: Node.js com `@mermaid-js/mermaid-cli`, para verificar a sintaxe dos diagramas, e um navegador Chromium, para recapturar imagens e slides.

```bash
git clone https://github.com/fabrizzioriccelli/1TIAO-ENTERPRISE-CHALLENGE-.git
cd 1TIAO-ENTERPRISE-CHALLENGE-
python -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/gerar_dados_sinteticos.py   # massa sintética e gabarito em data/sintetico/ (semente fixa)
python src/exemplos_calculados.py      # data/resultados/ e docs/anexos/exemplos-calculados.md
python src/gerar_graficos.py           # gráficos SVG em assets/graficos/
python src/gerar_visuais.py            # capa e wireframes (HTML) em assets/fontes/
python src/gerar_slides.py             # slides do vídeo (HTML) em assets/fontes/
python src/validar_entregaveis.py      # verificações automáticas da entrega
```

Os scripts são determinísticos: executá-los de novo reproduz os mesmos arquivos. As imagens PNG e o PDF dos slides são capturas das páginas HTML com um Chromium sem interface, por exemplo:

```bash
chromium --headless --no-sandbox --hide-scrollbars --window-size=1600,640 \
  --screenshot=assets/capa-frota-pulse.png "file://$PWD/assets/fontes/capa.html"
chromium --headless --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=docs/video/slides-apoio.pdf "file://$PWD/assets/fontes/slides.html"
```

Tamanhos de janela dos wireframes: `wf-01` 1440×900, `wf-02` 1440×1180 e `wf-03` 1100×1200.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>

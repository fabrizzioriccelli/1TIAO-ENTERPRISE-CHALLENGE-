# Declaração de uso de inteligência artificial

Este documento registra, de forma transparente, como uma ferramenta de IA generativa foi usada na produção desta entrega. Ele deve ser mantido atualizado pelo grupo.

**O que o enunciado diz.** "Nesta etapa inicial, o grupo pode utilizar ferramentas de IA para apoiar pesquisas, brainstorming e levantamento de alternativas técnicas. As escolhas poderão ser revistas ao longo das próximas Sprints, desde que as mudanças sejam justificadas e mantenham coerência com o problema." O uso registrado abaixo vai além desses três propósitos, porque a ferramenta também redigiu a primeira versão dos documentos, dos dados e dos scripts. Por isso o grupo deve apresentar esta declaração à tutoria e confirmar como o uso será considerado antes da entrega **[Pendência]**.

## 1. Ferramenta

| Item | Registro |
|---|---|
| Ferramenta | Claude Code (assistente de programação da Anthropic), em sessão na nuvem |
| Período | Outubro de 2026 |
| Quem operou | Fabrizzio Riccelli, integrante do grupo responsável pelo repositório (conta GitHub `fabrizzioriccelli`) |
| Identificação no histórico | Os commits feitos pela ferramenta têm o autor `Claude <noreply@anthropic.com>`. O histórico não foi reescrito, e a autoria não foi atribuída a integrantes |

## 2. O que foi feito com apoio da IA

A ferramenta recebeu o briefing oficial, o template da FIAP e um roteiro de instruções do grupo, e produziu **a primeira versão** de:

- toda a documentação em `docs/` (análise do problema, personas, matriz de User Stories, solução, modelagem, ingestão, diagnóstico, benchmarks, economia, IA, arquitetura, segurança, UX, roadmap, roteiro do vídeo, validação, teste adversarial e referências);
- o dicionário de dados, o gerador da massa sintética e os dados em `data/`;
- os scripts de cálculo, gráficos, visuais, slides e validação em `src/`;
- os diagramas, gráficos, wireframes, capa e slides em `assets/` e `docs/video/`;
- a animação do vídeo (sem voz), gerada por script a partir do roteiro; a narração é gravada por um integrante, como exige o enunciado;
- o README e o arquivo de links da entrega.

A ferramenta também fez buscas na web para conferir referências legais e bibliográficas. O nível de verificação de cada fonte está em [referências](referencias.md); várias fontes oficiais estavam bloqueadas no ambiente e foram conferidas apenas por busca.

## 3. Decisões tomadas pelo grupo

- Criar um repositório privado novo, sem misturar com outros projetos.
- Turma 1TIAO e estrutura "Challenge na raiz" do template.
- Commits diretamente na branch principal.
- Instruções gerais de conteúdo, restrições de segurança e de integridade acadêmica (não inventar dados, nomes, links ou resultados).

## 4. Limites e cuidados

- **Nenhum dado real** de clientes, pessoas ou empresas foi usado. Todos os números de frota são sintéticos e gerados por script com semente fixa.
- **Nenhuma entrevista, teste com usuário ou parceria** foi realizada ou simulada como real. Personas são hipotéticas.
- **Nenhum modelo de IA foi treinado.** A [estratégia de IA](estrategia-ia.md) descreve propostas para as próximas Sprints.
- Os cálculos foram feitos por código determinístico e reprodutível, não por geração de texto. O [validador](../src/validar_entregaveis.py) confere números citados na documentação contra os resultados calculados.
- Conteúdo jurídico serve para orientar requisitos e precisa de validação por profissional habilitado.

## 5. Responsabilidade do grupo

A IA acelera a produção, mas **não substitui o entendimento do grupo**. Antes da entrega, cada integrante deve:

1. Ler os documentos da sua área (ver papéis no [roadmap](roadmap.md#3-equipe-e-responsabilidades)) e ser capaz de explicá-los sem consulta.
2. Executar os scripts e conferir que os resultados batem com a documentação.
3. Responder às perguntas do [teste adversarial](teste-adversarial.md) com as próprias palavras.
4. Corrigir, reescrever ou remover o que não concordar, registrando a mudança em commit próprio.

Cartão K-021 do [Kanban](anexos/kanban.csv): nenhum artefato sai de "Em revisão" sem essa revisão.

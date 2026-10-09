# Relatório de validação automática

Gerado por [`src/validar_entregaveis.py`](../../src/validar_entregaveis.py). Não edite à mão: execute o script de novo.

Status: **OK** passou; **FALHA** precisa de correção; **AVISO** revisar; **PENDENTE** depende do grupo ou de ação externa; **MANUAL** exige conferência humana; **INFO** apenas registro.

| Status | Quantidade |
|---|---|
| OK | 40 |
| AVISO | 1 |
| PENDENTE | 3 |
| MANUAL | 1 |
| INFO | 1 |

| Grupo | Verificação | Status | Detalhe |
|---|---|---|---|
| 1. Dicionário | Colunas do dicionário | **OK** | 13 colunas |
| 1. Dicionário | Campos sem duplicidade | **OK** | 181 campos em 23 tabelas |
| 1. Dicionário | Atributos preenchidos (nome, descrição, tipo, unidade, obrigatoriedade, validação, origem, sensibilidade, exemplo, ausência) | **OK** | 0 atributos vazios |
| 1. Dicionário | Regra de máquina definida | **AVISO** | 3 campos sem regra de máquina (texto livre): despesas.descricao_original, manutencoes.oficina_codigo, recomendacoes.solucao_relacionada |
| 1. Dicionário | Tabelas da massa sintética documentadas | **OK** | 14 CSVs, todos no dicionário |
| 1. Dicionário | Colunas dos CSVs iguais às do dicionário (nome e ordem) | **OK** | 131 campos documentados nas 14 tabelas presentes |
| 2. Regras de máquina | Regras do dicionário aplicadas a todos os registros | **OK** | 175 regras em 48148 registros |
| 2. Regras de máquina | Violações explicadas pelo gabarito (erros injetados de propósito) | **OK** | 24 violações em registros de cenários planejados |
| 2. Regras de máquina | Violações fora do gabarito | **OK** | nenhuma |
| 3. Gabarito | Cenários G01 a G34, sem repetição | **OK** | 34 cenários; problema_dado 13, achado_negocio 8, justificavel 5, lacuna 6, controle_negativo 2 |
| 3. Gabarito | Registros do gabarito existem nos dados | **OK** | 848 referências |
| 3. Gabarito | Cenários com registros marcados | **OK** | todos |
| 3. Gabarito | Contagens de metadados.json iguais às dos CSVs | **OK** | 14 tabelas |
| 4. Links e âncoras | Links internos e âncoras | **OK** | 260 links internos em 22 arquivos |
| 4. Links e âncoras | Links externos | **MANUAL** | 11 endereços distintos; acesso não testado neste ambiente (rede restrita) |
| 5. Tabelas Markdown | Mesma quantidade de células em cada linha | **OK** | todas as tabelas |
| 6. Mermaid | Sintaxe dos diagramas (renderização com mermaid-cli) | **OK** | 9 diagramas renderizados sem erro |
| 7. Números citados | Valores-chave da documentação iguais aos calculados | **OK** | 11 afirmações conferidas |
| 7. Números citados | Valores monetários com centavos encontrados no anexo calculado | **OK** | todos localizados |
| 8. Dados sensíveis | CPF formatado | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | CNPJ formatado | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | Placa real (antiga ou Mercosul) | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | Chave privada | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | Token AWS | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | Token GitHub | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | Chave de API genérica | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | Senha em texto | **OK** | nenhuma ocorrência em 72 arquivos |
| 8. Dados sensíveis | E-mail | **OK** | nenhuma ocorrência em 72 arquivos |
| 9. Arquivos | Arquivos duplicados (mesmo conteúdo) | **OK** | 78 arquivos |
| 9. Arquivos | Codificação UTF-8 | **OK** | todos os textos |
| 9. Arquivos | Sem emojis fora dos títulos do template | **OK** | nenhum |
| 9. Arquivos | Pendências declaradas no texto | **INFO** | 24 marcações: README.md (7), docs/problema.md (7), docs/roadmap.md (3), docs/seguranca-lgpd.md (2), ENTREGA_SPRINT1_LINKS.txt (1), docs/arquitetura.md (1), docs/economia-recomendacoes.md (1), docs/user-stories.md (1), docs/uso-de-ia.md (1) |
| 10. Template e entrega | Seções do README do template | **OK** | 13 seções presentes |
| 10. Template e entrega | README concentra os itens do enunciado (4.1) | **OK** | 13 seções |
| 10. Template e entrega | README explica cada User Story selecionada | **OK** | 20 de 20 User Stories na tabela |
| 10. Template e entrega | Diagrama do fluxo do enunciado no README, na ordem pedida | **OK** | Entrada de dados → Tratamento e organização → Análise dos custos → Diagnóstico → Benchmark → Recomendações → Visualização e relatório |
| 10. Template e entrega | Responsabilidades por integrante | **PENDENTE** | depende do grupo |
| 10. Template e entrega | Observação do tutor removida | **OK** |  |
| 10. Template e entrega | Campo FIAP NEXT presente | **OK** |  |
| 10. Template e entrega | Decisão FIAP NEXT marcada | **PENDENTE** | depende do grupo |
| 10. Template e entrega | Integrantes e tutor | **OK** |  |
| 10. Template e entrega | Logo do template | **OK** |  |
| 10. Template e entrega | Pastas do template | **OK** |  |
| 10. Template e entrega | Arquivo de links: só repositório e vídeo | **OK** | 2 linhas |
| 10. Template e entrega | Link do vídeo publicado | **PENDENTE** | vídeo não gravado |
| 11. Reprodutibilidade | Massa regenerada idêntica à versionada | **OK** | 18 arquivos idênticos byte a byte |

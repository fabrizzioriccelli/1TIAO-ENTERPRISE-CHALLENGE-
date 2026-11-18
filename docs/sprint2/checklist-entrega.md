# Checklist da entrega da Sprint 2

Situação conferida em 18/11/2026. Um item só está "Atendido" quando há evidência no repositório ou em uma verificação executada.

| # | Item pedido | Situação | Evidência |
|---|---|---|---|
| 1 | Auditoria do projeto da Sprint 1 antes de evoluir | Atendido | [auditoria-sprint1.md](auditoria-sprint1.md) |
| 2 | Ingestão de CSV, TXT e JSON com pandas | Atendido | `src/frota_pulse/ingestao.py`; 12 arquivos lidos (log do pipeline) |
| 3 | Identificação da origem, ID comum do veículo, colunas, categorias, datas, unidades e ausentes padronizados | Atendido | `normalizacao.py`; [metodologia, seção 3](metodologia.md#3-normalização) |
| 4 | Exportação consolidada em CSV e JSON | Atendido | `data/processed/base_consolidada_veiculo_mes.csv`, `indicadores_veiculo.json` |
| 5 | Integração de cadastro, custos, km e telemetria por veículo e período | Atendido | `integracao.py`; 888 veículo-mês |
| 6 | Regras de qualidade com relatório (tipo, arquivo, registro, tratamento, justificativa), sem exclusão silenciosa, originais separados | Atendido | `outputs/reports/relatorio_qualidade.csv`; `data/raw/` intacto; teste `test_nenhum_registro_e_apagado` |
| 7 | Firmware ESP32 com velocidade, RPM, temperatura, combustível, ID do veículo, Serial e anomalias com LED e buzzer | Atendido | `src/esp32/firmware/telemetria_frota/`; [telemetria-esp32.md](telemetria-esp32.md) |
| 8 | CSV da telemetria e evidência de anomalias | Atendido | `data/telemetria/telemetria_esp32.csv`; [monitor_serial_demo.txt](evidencias/monitor_serial_demo.txt); gráfico 06 |
| 9 | Link do Wokwi e captura do circuito em execução | **Pendente** | Exige login no wokwi.com (cartão S2-18). Há o diagrama gerado do `diagram.json`, que não é captura do Wokwi |
| 10 | Compilação para o ESP32 real | **Não realizado** | Download das ferramentas bloqueado pela rede do ambiente; validado por compilação nativa e testes |
| 11 | Benchmark com grupos comparáveis, média, mediana, quartis, gaps com direção, rankings, gráficos e correlações | Atendido | `benchmark.py`; `outputs/reports/benchmark_grupos.csv`, rankings; gráficos 02 a 05 |
| 12 | Modelo supervisionado com rótulo, atributos, treino e teste, acurácia, exemplos certos e errados, sem vazamento | Atendido | [machine-learning.md](machine-learning.md); `outputs/predictions/`; testes do modelo |
| 13 | Diagnóstico por regras com limites justificados e comparação com o modelo | Atendido | [metodologia, seção 9](metodologia.md#9-diagnóstico-por-regras); `comparacao_regras_ml.csv` |
| 14 | Sem economia em R$ e sem motor de recomendações nesta Sprint | Atendido | Fora do código; previsto nos cartões S3-02 e S3-03 |
| 15 | Arquitetura e diagrama | Atendido | [arquitetura.md](arquitetura.md) |
| 16 | Testes reais e execução do pipeline completo | Atendido | 36 testes aprovados; pipeline em cerca de 6 s; [testes.md](testes.md) |
| 17 | README no template 2026 com os itens pedidos e a descrição em até 600 palavras | Atendido | `README.md`; validador (`src/validar_entregaveis.py`) sem falhas |
| 18 | Dicionário de dados da Sprint 2 | Atendido | `data/dicionario-dados-sprint2.csv` |
| 19 | Kanban da Sprint 2 com responsável, status, prioridade, dependências, entregável e pendências da Sprint 3 | Atendido | Trello (30 cartões) e [kanban-sprint2.csv](kanban-sprint2.csv) |
| 20 | Roteiro, storyboard, versão-base limpa e versão demonstrativa do vídeo | Atendido fora do repositório | Entregues ao grupo como arquivos; o material de vídeo não fica no GitHub por decisão do grupo |
| 21 | Vídeo narrado de até 5 minutos publicado no YouTube como não listado | **Pendente** | Depende da gravação da narração por um integrante (cartão S2-19) |
| 22 | Arquivo .txt com os links do repositório e do vídeo | Parcial | `ENTREGA_SPRINT2_LINKS.txt` com o repositório; vídeo marcado como pendente |
| 23 | Repositório privado com acesso de `fiap-tutoria` | Atendido | Lista de colaboradores do GitHub em 18/11/2026: `fiap-tutoria` com permissão de escrita |
| 24 | Acesso de todos os integrantes | **Pendente** | Guntooo e natashazont ainda não aparecem como colaboradores (cartão S2-21) |
| 25 | Revisão do grupo | **Pendente** | Cartão S2-20 |
| 26 | Entrega no portal da FIAP | **Pendente** | Cartão S2-22 |

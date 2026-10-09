# Segurança, privacidade e governança

Requisitos iniciais para as Sprints 2 a 4. Este documento não é parecer jurídico: as bases legais e os papéis de controlador e operador devem ser validados pelo jurídico e pelo encarregado de dados (DPO) da Sem Parar Empresas antes de qualquer piloto com dados reais **[Pendência]**.

## 1. Que dados são pessoais

A maior parte dos dados de frota é **dado empresarial**: valores, fornecedores, rotas, consumo. Não é dado pessoal, mas é **confidencial** (sigilo comercial do cliente). Alguns dados, porém, identificam ou podem identificar pessoas:

| Dado | Pessoal? | Por quê | Tratamento previsto |
|---|---|---|---|
| Nome e e-mail do usuário (representante do cliente) | Sim | Identifica pessoa natural | Mínimo necessário; base legal por finalidade |
| Condutor indicado em multa | Sim | Identifica o motorista | Só pseudônimo (`condutor_token`) na base analítica; nome e CNH não são coletados |
| Placa do veículo | Indiretamente | Veículo de uso exclusivo de um empregado pode identificá-lo | Cifrada na camada bruta; pseudônimo por HMAC com chave do cliente na análise |
| Localização (EXIF de fotos, telemetria) | Indiretamente | Revela rotina de uma pessoa | EXIF removido na recepção; telemetria só em agregados de km |
| Descrição livre de documentos e mensagens | Pode conter | Texto pode citar nomes | Mascaramento na exibição; não usado para treinar modelos sem autorização |
| CNPJ, razão social, custos e contratos | Não (pessoa jurídica) | - | Confidencial: isolamento por cliente e acesso por perfil |

## 2. Requisitos de segurança

| Código | Tema | Requisito |
|---|---|---|
| SEG-01 | Autenticação | Login por provedor de identidade (OIDC). Senhas longas e verificadas contra listas de senhas vazadas, sem regras arbitrárias de composição; mínimo de 15 caracteres quando a senha for o único fator, conforme NIST SP 800-63B-4. MFA obrigatório para perfis administrativos e da Sem Parar Empresas |
| SEG-02 | Autorização | Perfis `gestor_frota`, `financeiro`, `admin_cliente`, `analista_spe` e `admin_plataforma`, com permissões por ação e sempre limitadas ao cliente; analistas da Sem Parar Empresas veem só dados agregados ou de clientes com autorização registrada |
| SEG-03 | Isolamento entre clientes | `empresa_id` em todas as tabelas; segurança em nível de linha no PostgreSQL; teste automatizado de vazamento a cada versão |
| SEG-04 | Criptografia em trânsito | TLS 1.2 ou superior em todas as conexões, inclusive internas |
| SEG-05 | Criptografia em repouso | Disco e armazenamento de objetos cifrados (AES-256); cifra de campo para placa e chaves de pseudonimização em cofre |
| SEG-06 | Proteção de arquivos | Limite de tamanho; verificação de tipo real; antivírus; remoção de metadados; armazenamento fora do servidor web; acesso por URL temporária |
| SEG-07 | Integridade | Hash SHA-256 de cada arquivo; camada bruta imutável; diagnóstico com versão da metodologia, reproduzível |
| SEG-08 | Auditoria | Registro somente de inclusão (*append-only*) de login, envio, correção, exportação, mudança de permissão, mudança de consentimento e toda consulta da Sem Parar Empresas a dados de cliente |
| SEG-09 | Retenção e exclusão | Prazos por tipo de dado (seção 5); exclusão a pedido ou ao fim do contrato, salvo obrigação legal |
| SEG-10 | Backup | Diário, cifrado, em local separado; teste de restauração trimestral; metas iniciais: perda máxima de 24 horas e recuperação em até 8 horas |
| SEG-11 | Credenciais | Segredos em cofre do provedor; rotação periódica; nunca no repositório; varredura de segredos no pipeline |
| SEG-12 | Desenvolvimento seguro | OWASP ASVS 5.0 (nível 2) como lista de verificação; análise estática e de dependências; teste de intrusão antes do piloto |
| SEG-13 | IA e terceiros | Contrato sem retenção nem treinamento com dados do cliente; conteúdo de documentos tratado como dado não confiável ([estratégia de IA](estrategia-ia.md)) |
| SEG-14 | Incidentes | Plano de resposta com papéis, prazos e comunicação à ANPD e aos titulares conforme a regulamentação vigente |

## 3. LGPD aplicada

**Princípios (Lei nº 13.709/2018, art. 6º):**

| Princípio | Como o produto cumpre |
|---|---|
| Finalidade | Cada uso tem finalidade registrada: prestação do serviço, contato comercial, benchmark agregado |
| Adequação | Dado usado só na finalidade declarada; o painel comercial não acessa diagnósticos sem autorização |
| Necessidade | Nome e CNH de condutores não são coletados; placa e condutor viram pseudônimos; EXIF removido |
| Livre acesso | Usuário vê e exporta seus dados e suas preferências |
| Qualidade dos dados | Status do valor, revisão humana e correção rastreável |
| Transparência | Aviso de privacidade em linguagem simples, por finalidade, no momento da coleta |
| Segurança | Requisitos SEG-01 a SEG-14 |
| Prevenção | Avaliação de impacto antes de novas finalidades; testes de vazamento |
| Não discriminação | Sem pontuação individual de motoristas; achados tratam veículos e processos, não pessoas |
| Responsabilização e prestação de contas | Registro das operações de tratamento, auditoria e versão das regras |

**Papéis (a validar com o jurídico).** Conforme o guia da ANPD sobre agentes de tratamento:

- o **cliente** é controlador dos dados de seus condutores e empregados;
- a **plataforma** atua como operadora ao processar o diagnóstico em nome do cliente;
- para finalidades próprias, como contato comercial, a **Sem Parar Empresas** passa a ser controladora dos dados de contato do representante, com base legal própria.

**Bases legais por finalidade (proposta, art. 7º):**

| Finalidade | Dados | Base legal proposta | Observação |
|---|---|---|---|
| Conta e prestação do serviço | Nome e e-mail do usuário | Execução de contrato (art. 7º, V) | Necessário para usar a ferramenta |
| Diagnóstico com dados de condutores | Pseudônimos de condutores | Definida pelo cliente, como controlador; a plataforma segue suas instruções | O contrato com o cliente registra a instrução |
| Contato comercial (US-SP-02, US-SP-06) | Contato do representante e resumo de oportunidades | Consentimento específico (art. 7º, I) **ou** legítimo interesse (art. 7º, IX e art. 10) com teste de balanceamento documentado e opção simples de oposição | Recomendação do grupo: consentimento específico, separado do aceite dos termos de uso |
| Benchmark agregado (US-SP-03) | Indicadores por veículo·mês, sem identificação | Dados anonimizados não são dados pessoais (art. 12), desde que a anonimização não seja reversível com esforço razoável; para o sigilo empresarial, autorização contratual do cliente | Grupos com 10 empresas ou mais e regra de dominância ([benchmarks](benchmarks.md#3-quando-não-comparar)) |
| Segurança e auditoria | Registros de acesso | Legítimo interesse ou cumprimento de obrigação, conforme o caso | Prazo de retenção definido |

**Outros pontos:** atendimento aos direitos do titular (art. 18) por canal no próprio produto; registro das operações de tratamento (art. 37); relatório de impacto à proteção de dados (art. 38) recomendado antes do uso comercial; e, se houver serviço de nuvem ou de IA fora do Brasil, observância das regras de transferência internacional (art. 33).

## 4. Finalidades comerciais: leads e benchmarks

US-SP-02 e US-SP-06 pedem que a Sem Parar Empresas identifique oportunidades e mantenha contato com clientes. O desenho proposto atende a essa necessidade sem tratar a coleta como irrestrita:

1. **Duas autorizações separadas, opcionais e revogáveis:** "Quero ser contatado pela Sem Parar Empresas sobre soluções relacionadas ao meu diagnóstico" e "Autorizo o uso agregado e anônimo dos meus indicadores para melhorar as referências da calculadora".
2. **Contato de serviço sempre registrado**, para avisos sobre a conta e o próprio diagnóstico. Não se usa para oferta.
3. **Painel comercial** (F16) mostra empresa, tipo de oportunidade, valor estimado e contato **somente** com a primeira autorização ativa; sem ela, só contagens agregadas. Toda consulta fica na auditoria.
4. **Qualificação do lead** usa dados da empresa (porte, oportunidades, estágio de evidência). Não há perfilamento de pessoas.
5. **Revogação** retira o cliente do painel em até 24 horas (meta) e é registrada com data e versão do termo.
6. **Transparência na recomendação:** quando uma solução da Sem Parar Empresas aparece, o texto diz que é uma solução do portfólio e que não há garantia de economia ([economia e recomendações](economia-recomendacoes.md#7-relação-com-o-portfólio-sem-parar-empresas)).

Com isso, "sempre ter as informações do cliente" (US-SP-06) é atendido para o relacionamento de serviço e, para fins comerciais, na medida da autorização. Essa diferença está registrada como atendimento parcial por decisão em [User Stories](user-stories.md#us-sp-06).

## 5. Retenção e exclusão (proposta)

| Dado | Prazo proposto | Depois do prazo |
|---|---|---|
| Arquivos brutos enviados | 12 meses após o processamento, ou o prazo do contrato | Exclusão; o hash permanece para detectar reenvio |
| Base analítica do cliente | Enquanto durar o contrato | Exclusão em até 30 dias após o encerramento, salvo obrigação legal |
| Indicadores anonimizados do benchmark | Enquanto forem úteis | Não identificam o cliente; revisão anual da anonimização |
| Registros de auditoria | 2 anos (hipótese, a validar com o jurídico) | Exclusão |
| Backups | Rotação de 35 dias | Expiram automaticamente; exclusões são reaplicadas na restauração |
| Consentimentos e revogações | Enquanto houver tratamento e pelo prazo de prescrição aplicável | Mantidos como prova |

Os prazos são propostas de produto, a confirmar com o jurídico; não decorrem de obrigação legal verificada nesta Sprint.

## 6. Governança

| Tema | Regra |
|---|---|
| Metodologia | Toda mudança em indicador, regra, premissa ou catálogo gera nova versão, nota de mudança e reprocessamento dos testes |
| Catálogo de recomendações | Inclusão ou alteração revisada pelo grupo e pela Sem Parar Empresas; associação ao portfólio sempre por regra |
| Modelos de IA | Registro de versão, dados de avaliação, métricas e limiar de aceite antes de produção |
| Acesso interno | Revisão trimestral de perfis; acesso de suporte a dados do cliente só com chamado e registro |
| Dados no repositório | Proibido versionar dados reais, credenciais ou documentos de clientes |

## 7. Situação do repositório

- Só há dados **sintéticos**. CNPJ e placa não foram gerados; condutores, autos de infração e apólices aparecem como pseudônimos com prefixo (`MOT-`, `AIT-`, `APL-`).
- Não há credenciais, tokens ou chaves. O validador ([`src/validar_entregaveis.py`](../src/validar_entregaveis.py)) procura padrões de CPF, CNPJ, placa, e-mail, chaves de API e chaves privadas em todos os arquivos versionados.
- O repositório é privado. O acesso do perfil `fiap-tutoria` deve ser concedido pelo dono do repositório **[Pendência]**.

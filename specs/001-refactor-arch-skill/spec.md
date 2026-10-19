# Feature Specification: Skill refactor-arch — Auditoria e Refatoração Arquitetural Automatizada

**Feature Branch**: `dev` (sem branch dedicada; diretório da feature: `specs/001-refactor-arch-skill`)

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Crie a especificação para desenvolvimento da skill seguindo os critérios em @README.md e os princípios da constituição."

**Fontes normativas**: enunciado do desafio (`README.md` da raiz, commit `6d1ce62`) e
`.specify/memory/constitution.md` v2.2.0. Nomes, caminhos e mínimos quantitativos citados nesta
spec são **restrições impostas pelo enunciado**, não escolhas de implementação.

## Clarifications

### Session 2026-10-19

- Q: O relatório da Fase 2 é salvo manualmente pelo autor? → A: Não. A skill grava
  automaticamente o relatório em `reports/` ao final da Fase 2; não existe passo manual.
- Q: O que acontece quando a Fase 3 gera erros? → A: A execução é uma falha da skill. O código é
  revertido, a skill é atualizada e só então reexecutada, repetindo até uma execução sem erros.
  Reexecutar a skill sem alterar seu conteúdo após uma falha não é permitido.
- Q: Ao final da Fase 3, todos os findings precisam ser eliminados ou só os CRITICAL/HIGH? → A:
  Todos (CRITICAL a LOW). Uma reauditoria pós-refatoração contra o catálogo DEVE retornar zero
  anti-patterns; qualquer finding remanescente torna a execução uma falha.
- Q: A evidência de validação da Fase 3 é salva pela skill ou capturada manualmente? → A: Salva
  pela skill. Ao fim da Fase 3 (sucesso ou falha), a skill grava
  `evidence/validation-project-N.md` na raiz do repositório (mesma resolução de `N` dos
  relatórios); o README referencia esses arquivos.
- Q: A preservação do comportamento dos endpoints é comparada com respostas reais do original ou
  com o que o código indica? → A: Com respostas reais. No início da Fase 3 (após a confirmação e
  antes de qualquer modificação), a skill sobe a aplicação original, exercita todos os endpoints
  e grava status e formato de resposta como linha de base de comportamento; encerra a aplicação e
  limpa os artefatos dessa execução. Após a refatoração, compara contra essa linha de base de comportamento. Se o
  original não iniciar, usa o comportamento inferido do código e registra isso na evidência.
- Q: Onde a skill instala as dependências para subir as aplicações na Fase 3? → A: Em um ambiente
  isolado dentro do diretório do projeto, pelo mecanismo padrão da stack (ex.: ambiente virtual
  em Python, pasta local de dependências em Node.js), ignorado pelo git e preservado pela
  reversão; nunca no ambiente global da máquina.

## User Scenarios & Testing *(mandatory)*

**Atores**

- **Autor da skill** — aluno que cria, executa e itera a skill e entrega o repositório.
- **Avaliador** — professor/corretor que verifica o repositório contra os critérios de aceite.
- **Agente** — o assistente de IA (Claude Code) que executa a skill a partir do comando
  `/refactor-arch` dentro de um projeto-alvo.

### User Story 1 - Auditar um projeto legado sem alterá-lo (Priority: P1)

O autor abre um projeto-alvo e invoca `/refactor-arch`. O agente analisa a codebase, imprime um
resumo do projeto (linguagem, framework, dependências, domínio, arquitetura, quantidade de
arquivos, tabelas/entidades de dados) e, em seguida, um relatório de auditoria com todos os
problemas encontrados, cada um com severidade e localização exata. O relatório é gravado
automaticamente em `reports/`. Ao final, o agente pausa e pergunta se deve prosseguir com a
refatoração. Até essa resposta, nenhum arquivo do projeto foi alterado.

**Why this priority**: é o núcleo de valor da skill e cobre 3 dos 4 critérios de aceite
obrigatórios (detecção de stack, ≥ 5 findings, ≥ 1 CRITICAL/HIGH). Sozinha já entrega um
diagnóstico útil, seguro e arquivado.

**Independent Test**: invocar a skill em `code-smells-project/`, responder "n" na pausa e
verificar (a) o resumo da Fase 1 contra o código real, (b) o relatório contra o template e contra
a Análise Manual, (c) que o arquivo em `reports/` é idêntico ao relatório impresso e (d) que o
working tree do projeto permanece sem alterações.

**Acceptance Scenarios**:

1. **Given** um projeto-alvo no estado original, **When** o autor invoca `/refactor-arch`,
   **Then** o agente imprime o bloco `PHASE 1: PROJECT ANALYSIS` com linguagem, framework,
   dependências, domínio, arquitetura, número de arquivos-fonte e tabelas/entidades, todos
   correspondentes à realidade do projeto.
2. **Given** a Fase 1 concluída, **When** o agente executa a Fase 2, **Then** imprime o bloco
   `ARCHITECTURE AUDIT REPORT` no formato do template de relatório, com resumo por severidade,
   findings ordenados de CRITICAL a LOW, cada um com arquivo e linha(s) exatos, descrição,
   impacto e recomendação, e o total de findings.
3. **Given** o relatório impresso, **When** a Fase 2 termina, **Then** a skill grava o relatório
   em `reports/audit-project-N.md` na raiz do repositório, com conteúdo idêntico ao impresso, e
   informa o caminho gravado — sem nenhuma ação manual do autor.
4. **Given** o relatório gravado, **When** a Fase 2 termina, **Then** o agente pergunta
   `Proceed with refactoring (Phase 3)? [y/n]` e aguarda a resposta sem executar mais nada.
5. **Given** a pergunta de confirmação, **When** o autor responde algo diferente de uma
   confirmação explícita, **Then** o agente encerra e nenhum arquivo do projeto foi criado,
   alterado ou removido (apenas o relatório em `reports/` existe).
6. **Given** a Análise Manual documentada no README, **When** o relatório é comparado a ela,
   **Then** pelo menos 5 dos problemas documentados manualmente aparecem como findings.
7. **Given** um projeto que usa APIs obsoletas, **When** a Fase 2 roda, **Then** cada uso é
   reportado como finding com o equivalente moderno recomendado.
8. **Given** um projeto com alterações não commitadas fora de `.claude/`, **When** a Fase 2
   termina, **Then** no lugar da pergunta de confirmação a skill imprime a mensagem de bloqueio
   com o motivo (sem ponto de restauração), encerra sem iniciar a Fase 3 e orienta o autor a
   commitar ou descartar essas alterações.

---

### User Story 2 - Refatorar para MVC com validação comprovada e reversível (Priority: P2)

Após revisar o relatório, o autor confirma. O agente reestrutura o projeto para o padrão MVC
(config, models, views/routes, controllers, error handling centralizado, entry point claro),
eliminando os problemas reportados, e em seguida valida que a aplicação inicia e que todos os
endpoints originais continuam respondendo. Se a validação passa, imprime a nova estrutura e o
resultado. Se falha, a execução é declarada como falha da skill, com diagnóstico, e o projeto pode
ser revertido ao estado anterior.

**Why this priority**: entrega o critério de aceite "aplicação funciona após refatoração" e o
código refatorado que deve ser commitado; depende da Fase 2 para saber o que corrigir.

**Independent Test**: em um projeto auditado, confirmar com "y"; depois iniciar a aplicação com o
comando documentado e exercitar todos os endpoints originais, comparando com a linha de base de
comportamento. Forçar uma falha de validação e confirmar que a reversão devolve o projeto ao
estado anterior.

**Acceptance Scenarios**:

1. **Given** a confirmação explícita do autor e um ponto de restauração válido, **When** a Fase 3
   inicia, **Then** antes de qualquer modificação a skill sobe a aplicação original, exercita
   todos os endpoints inventariados, grava a linha de base de comportamento (status e formato de
   cada resposta), encerra a aplicação e remove os artefatos gerados por essa execução; em
   seguida o projeto passa a ter camadas separadas de configuração, models,
   views/routes, controllers, tratamento centralizado de erros e um entry point claro
   (composition root).
2. **Given** a refatoração concluída, **When** o agente valida, **Then** a aplicação inicia sem
   erros, cada endpoint inventariado na Fase 1 é exercitado e responde com o mesmo status e
   formato de resposta registrados na linha de base de comportamento capturada do original, e a
   reauditoria contra o catálogo encontra zero anti-patterns.
3. **Given** um finding de segurança cuja correção altera a resposta (ex.: deixar de expor um
   dado sensível), **When** a Fase 3 o corrige, **Then** a mudança de contrato é declarada no
   resumo da Fase 3.
4. **Given** uma falha em qualquer verificação da validação, **When** o agente a detecta,
   **Then** ele não remenda o código gerado: interrompe, declara a execução como **FALHA**,
   imprime o diagnóstico (erro observado, transformação ou arquivo de referência que o originou,
   lacuna provável na skill) e oferece reverter o projeto.
5. **Given** a oferta de reversão aceita, **When** o agente reverte, **Then** o diretório do
   projeto volta exatamente ao ponto de restauração, sem afetar a pasta `.claude/` (incluindo a
   skill), `reports/` nem `evidence/`.
6. **Given** o fim da Fase 3 (sucesso ou falha), **When** o agente conclui a validação, **Then**
   grava `evidence/validation-project-N.md` com o resultado, o boot, as respostas dos endpoints e
   a reauditoria, sem nenhuma ação manual do autor.
7. **Given** o resumo `PHASE 3: REFACTORING COMPLETE`, **When** o autor o lê, **Then** ele contém a
   nova árvore de diretórios e a lista de verificações de validação com seus resultados.
8. **Given** valores sensíveis hardcoded no original, **When** a Fase 3 termina, **Then** eles
   foram movidos para configuração lida do ambiente, e a aplicação continua iniciando localmente
   seguindo as instruções documentadas.

---

### User Story 3 - Iterar e reutilizar a mesma skill em outra stack e em projeto parcialmente organizado (Priority: P3)

O autor copia a pasta da skill, sem modificações, para `ecommerce-api-legacy/` (Node.js/Express) e
`task-manager-api/` (Python/Flask com camadas parciais) e executa as 3 fases em cada um. Sempre que
uma execução falha, o autor segue o ciclo reverter → atualizar a skill → reexecutar, até obter uma
execução limpa em cada projeto. A skill detecta corretamente cada stack e domínio, encontra
problemas também no projeto já organizado e adapta a refatoração ao que já existe.

**Why this priority**: prova o requisito de agnosticismo e garante que o resultado final venha da
skill, não de correções manuais; os critérios de aceite exigem 3/3 projetos. Depende das
histórias 1 e 2 estarem funcionando em um projeto.

**Independent Test**: comparar as 3 cópias da skill (devem ser idênticas), executar a skill em
cada projeto a partir da linha de base do código aplicando o checklist do enunciado e conferir no registro
de iterações que cada reexecução após falha usou uma versão diferente da skill.

**Acceptance Scenarios**:

1. **Given** cópias idênticas da skill nos 3 projetos, **When** a skill roda em
   `ecommerce-api-legacy/`, **Then** a Fase 1 identifica JavaScript/Node.js com Express, o
   domínio LMS com checkout, e as 3 fases completam com a aplicação funcionando.
2. **Given** `task-manager-api/`, **When** a skill roda, **Then** a Fase 1 identifica
   Python/Flask e o domínio de Task Manager, e a Fase 2 encontra ≥ 5 findings, incluindo ≥ 1
   CRITICAL ou HIGH, apesar da separação de camadas existente.
3. **Given** um projeto com camadas parcialmente adequadas, **When** a Fase 3 executa, **Then** o
   que já está adequado é preservado, apenas violações reais são corrigidas, e mudanças
   estruturais necessárias são propostas no relatório e executadas.
4. **Given** uma execução que falhou, **When** o autor itera, **Then** ele reverte o projeto,
   corrige a skill de forma genérica na cópia canônica, commita a alteração, re-sincroniza as
   cópias e reexecuta a partir da linha de base do código em todos os projetos afetados.
5. **Given** uma execução que falhou e uma skill ainda inalterada, **When** o autor considera
   reexecutar, **Then** a reexecução não é permitida — exceto quando a falha foi comprovadamente
   externa à skill (ex.: porta ocupada, runtime ausente) e registrada como tal.
6. **Given** uma execução limpa, **When** o autor a aceita, **Then** o código refatorado é
   commitado sem nenhuma edição manual posterior.

---

### User Story 4 - Documentar e entregar o resultado para avaliação (Priority: P4)

O autor registra a Análise Manual dos 3 projetos, commita os relatórios gravados pela skill e o
código refatorado de cada projeto, e completa o README com as seções exigidas, incluindo o
histórico de iterações, de modo que o avaliador consiga verificar todos os critérios apenas
navegando pelo repositório e, se quiser, reproduzir a execução.

**Why this priority**: sem a documentação e as evidências, a avaliação não consegue confirmar os
critérios; a Análise Manual também é a base para verificar a cobertura da Fase 2 (US1, cenário 6).

**Independent Test**: um leitor sem contexto prévio abre o repositório e localiza: Análise
Manual, 3 relatórios, código refatorado commitado, checklist de validação preenchido por projeto,
evidências de execução, histórico de iterações e instruções de como executar.

**Acceptance Scenarios**:

1. **Given** os 3 projetos originais, **When** a Análise Manual é concluída, **Then** o README
   lista, para cada projeto, ≥ 5 problemas com arquivo/linha, severidade e justificativa,
   incluindo ≥ 1 CRITICAL ou HIGH, ≥ 2 MEDIUM e ≥ 2 LOW.
2. **Given** as execuções limpas nos 3 projetos, **When** o avaliador abre `reports/`, **Then**
   encontra `audit-project-1.md` (code-smells-project), `audit-project-2.md`
   (ecommerce-api-legacy) e `audit-project-3.md` (task-manager-api), gravados pela skill nas
   execuções aceitas.
3. **Given** as 3 refatorações concluídas, **When** o avaliador lê o README, **Then** encontra as
   seções "Análise Manual", "Construção da Skill" (incluindo desafios e o histórico de iterações),
   "Resultados" e "Como Executar" com todo o conteúdo exigido pelo enunciado.
4. **Given** o repositório final, **When** o avaliador inspeciona o histórico, **Then** o código
   refatorado de cada projeto está commitado, cada alteração da skill tem seu próprio commit e o
   estado original continua recuperável.

---

### Edge Cases

- **Resposta ambígua ou negativa na pausa** (ex.: "talvez", "n", silêncio): tratada como não
  confirmação; nenhuma modificação no projeto; o relatório já gravado permanece.
- **Projeto fora de um repositório git ou com alterações pendentes**: não há ponto de restauração
  confiável; a skill informa na pergunta de confirmação e não executa a Fase 3. O relatório é
  gravado em `reports/` dentro do diretório atual quando não há raiz de repositório.
- **Número do relatório**: resolvido por argumento opcional da invocação; senão, reutiliza o
  relatório existente do mesmo projeto (reexecução sobrescreve); senão, próximo número livre. Com
  a ordem de execução do enunciado (1 → 2 → 3) e sem argumentos, os nomes exigidos são obtidos.
- **Dependências do projeto não instaladas**: Fases 1 e 2 funcionam apenas lendo arquivos; a
  instalação no ambiente isolado do projeto, usando o manifesto do próprio projeto, só ocorre na
  Fase 3, após confirmação. Se o ambiente isolado já existir, é reutilizado.
- **Ambiente isolado não ignorado pelo git**: a skill verifica, antes de criá-lo, que o caminho
  do ambiente isolado é ignorado pelo git; se não for, informa e não o cria dentro do projeto
  (falha externa registrada), para nunca commitar dependências.
- **Pré-requisitos de boot** (ex.: popular o banco antes da primeira execução): a validação segue
  os passos de execução documentados no projeto (README, scripts do manifesto) e o projeto
  refatorado mantém esses passos funcionando ou os documenta.
- **Endpoints que exigem corpo, parâmetros ou autenticação**: a validação usa requisições de
  exemplo existentes no projeto ou deriva payloads válidos do código; endpoints que alteram dados
  são exercitados em ordem que não invalide os demais testes.
- **Porta ocupada ou processo remanescente** (ex.: no macOS o Receptor AirPlay ocupa a porta
  5000): antes de iniciar a aplicação, a skill verifica que a porta está livre; respostas de
  outro processo nunca contam como boot bem sucedido. Se a porta estiver ocupada e não houver
  forma de mudá-la sem editar o código (variável de ambiente já suportada ou opção de linha de
  comando do framework), a execução para como falha externa com orientação de correção, que
  permite reexecutar sem alterar a skill. A skill encerra todos os processos que iniciou,
  inclusive após falha.
- **Aplicação original não inicia** (legado quebrado ou dependência ausente): a linha de base de
  comportamento é
  inferida do código, marcada como "inferida" na evidência; a refatoração ainda precisa subir e
  responder conforme essa referência.
- **Respostas não determinísticas** (ids gerados, timestamps, ordem de listas): a comparação
  considera status e estrutura/campos da resposta, não valores voláteis.
- **Banco em memória vs. em arquivo**: a validação não depende de dados criados em execuções
  anteriores; artefatos de runtime gerados por cada execução da aplicação (ex.: banco local) são
  detectados e removidos logo após essa execução, antes da comparação seguinte e de qualquer
  reversão.
- **Nenhuma API deprecated presente**: o relatório declara que nenhuma foi encontrada, sem
  inventar findings.
- **Mesmo problema em vários pontos**: cada ocorrência é localizada; ocorrências agrupadas em um
  finding listam todas as localizações e são contadas uma única vez.
- **Skill invocada em projeto já refatorado**: a skill audita o estado atual normalmente; para
  reexecuções avaliativas, o autor parte da linha de base do código.
- **Finding remanescente na reauditoria** (de qualquer severidade, inclusive LOW): a execução é
  falha; o diagnóstico aponta o finding e o padrão do playbook que não o eliminou.
- **Erro durante a própria Fase 3, antes da validação** (ex.: transformação não aplicável):
  tratado como falha da execução — diagnóstico + oferta de reversão.
- **Script utilitário da skill falha ou não é suportado no ambiente**: o agente segue o
  procedimento manual equivalente descrito na skill.
- **Projeto em stack não coberta explicitamente**: as heurísticas genéricas ainda produzem o
  resumo; campos não identificáveis são marcados como "não detectado", sem chute.

## Requirements *(mandatory)*

### Functional Requirements

**Identidade e anatomia da skill**

- **FR-001**: A skill MUST se chamar `refactor-arch`, residir em `.claude/skills/refactor-arch/`
  e ter como arquivo principal `SKILL.md`, invocável pelo comando `/refactor-arch` sem argumentos
  (argumento opcional permitido apenas para o número do relatório).
- **FR-002**: `SKILL.md` MUST conter metadados de identificação (`name` igual ao nome do
  diretório; `description` em terceira pessoa, ≤ 1024 caracteres, dizendo o que a skill faz e
  quando usá-la) e um corpo com menos de 500 linhas.
- **FR-003**: `SKILL.md` MUST orquestrar as 3 fases, indicando os critérios de saída de cada uma
  e quando consultar cada arquivo de referência; o conhecimento de domínio MUST ficar nos
  arquivos de referência, referenciados diretamente a partir do `SKILL.md` (um nível).
- **FR-004**: Arquivos de referência MUST ser Markdown; os que tiverem mais de 100 linhas MUST
  abrir com sumário. A terminologia MUST ser consistente entre todos os arquivos.
- **FR-005**: A skill MUST fornecer checklists de progresso para o agente acompanhar cada fase.

**Fase 1 — Análise**

- **FR-006**: A skill MUST detectar linguagem, framework (com versão quando declarada),
  dependências principais, banco de dados, domínio da aplicação, arquitetura atual, número de
  arquivos-fonte analisados e tabelas/entidades de dados.
- **FR-007**: A skill MUST inventariar todos os endpoints existentes (método e path) para uso na
  validação da Fase 3.
- **FR-008**: A skill MUST imprimir o resumo no formato de banner `PHASE 1: PROJECT ANALYSIS`
  do enunciado.
- **FR-009**: A skill MUST verificar, sem efeitos colaterais, se existe ponto de restauração
  (projeto sob controle de versão, sem alterações pendentes fora de `.claude/`).

**Fase 2 — Auditoria**

- **FR-010**: A skill MUST comparar o código contra o catálogo de anti-patterns e produzir o
  relatório `ARCHITECTURE AUDIT REPORT` conforme o template de relatório: cabeçalho
  (projeto, stack, arquivos, linhas), resumo por severidade, findings e total.
- **FR-011**: Cada finding MUST conter severidade, nome do anti-pattern, arquivo e linha(s)
  exatos, descrição, impacto e recomendação; as linhas citadas MUST existir e corresponder ao
  problema.
- **FR-012**: Findings MUST estar ordenados de CRITICAL → HIGH → MEDIUM → LOW, e as contagens do
  resumo MUST bater com a lista.
- **FR-013**: A skill MUST detectar uso de APIs deprecated e recomendar o equivalente moderno.
- **FR-014**: A skill MUST NOT reportar findings sem evidência no código.
- **FR-015**: Ao final da Fase 2, a skill MUST gravar automaticamente o relatório em
  `reports/audit-project-N.md` na raiz do repositório (criando a pasta se necessário), com
  conteúdo idêntico ao impresso, e informar o caminho gravado.
- **FR-016**: O número `N` MUST ser resolvido de forma genérica: argumento opcional da invocação;
  senão, relatório existente do mesmo projeto (identificado pelo cabeçalho), que é sobrescrito;
  senão, próximo número sequencial livre.
- **FR-017**: Após gravar o relatório, se houver ponto de restauração, a skill MUST pausar e
  solicitar confirmação explícita (`Proceed with refactoring (Phase 3)? [y/n]`); apenas
  confirmação afirmativa libera a Fase 3. Sem ponto de restauração, a skill MUST imprimir a
  mensagem de bloqueio no lugar da pergunta e encerrar sem iniciar a Fase 3.
- **FR-018**: As Fases 1 e 2 MUST ser somente-leitura em relação ao projeto: nenhum arquivo do
  projeto criado, alterado, movido ou removido; a única escrita permitida é o relatório em
  `reports/`.

**Fase 3 — Refatoração e validação**

- **FR-019**: A skill MUST reestruturar o projeto para MVC com: módulo de configuração sem
  valores sensíveis hardcoded, models que abstraem o acesso a dados, views/routes restritas a
  roteamento/apresentação, controllers que concentram o fluxo da aplicação, tratamento de erros
  centralizado e entry point claro.
- **FR-020**: A skill MUST eliminar os problemas reportados aplicando os padrões do playbook e
  MUST adaptar a transformação ao nível de organização existente (criar camadas em monolitos;
  preservar e corrigir em projetos parcialmente organizados).
- **FR-021**: A skill MUST preservar o contrato externo dos endpoints originais (método, path,
  parâmetros, status e formato de resposta), exceto quando a própria correção de segurança
  exigir mudança, que MUST ser declarada no resumo e na evidência.
- **FR-022**: Na Fase 3, a skill MUST instalar as dependências declaradas no manifesto do
  projeto apenas em um ambiente isolado dentro do diretório do projeto, usando o mecanismo padrão
  da stack, ignorado pelo git; MUST NOT instalar no ambiente global ou do usuário. O ambiente
  isolado MUST ser reutilizado quando já existir e MUST ser preservado pela reversão.
- **FR-023**: No início da Fase 3, após a confirmação e antes de qualquer modificação, a skill
  MUST capturar a linha de base de comportamento: subir a aplicação original seguindo seus passos
  de execução documentados, exercitar todos os endpoints inventariados, registrar status e
  formato (estrutura/campos) de cada resposta, encerrar a aplicação e remover os artefatos
  gerados por essa execução. Se o original não iniciar, a skill MUST usar o comportamento
  inferido do código como referência e registrar esse fato na evidência.
- **FR-024**: A Fase 3 MUST NOT alterar a pasta `.claude/` (incluindo a própria skill) nem
  `reports/`; fora do diretório do projeto, a única escrita permitida é o arquivo de evidência em
  `evidence/`.
- **FR-025**: A skill MUST validar o resultado (a) iniciando a aplicação, (b) exercitando todos
  os endpoints inventariados e comparando status e formato de cada resposta com a linha de base
  de comportamento (divergência não declarada como correção de segurança é falha) e (c) reauditando o código refatorado contra o catálogo, que MUST
  retornar zero anti-patterns de qualquer severidade; a skill MUST NOT declarar sucesso sem
  evidência das três verificações.
- **FR-026**: Em qualquer erro na Fase 3 (durante a transformação ou na validação), a skill MUST
  NOT remendar o código gerado; MUST interromper, declarar a execução como **FALHA** e imprimir
  diagnóstico com o erro observado, a transformação/arquivo de referência que o originou e a
  lacuna provável na skill.
- **FR-027**: Após uma falha, a skill MUST oferecer reverter o projeto ao ponto de restauração;
  a reversão MUST restringir-se ao diretório do projeto, removendo arquivos criados e restaurando
  os alterados, e MUST preservar `.claude/`, `reports/`, `evidence/` e o ambiente isolado de
  dependências.
- **FR-028**: A skill MUST encerrar todos os processos que iniciar para validação, inclusive em
  caso de falha.
- **FR-029**: Antes de iniciar a aplicação (original ou refatorada), a skill MUST verificar que a
  porta usada está livre e MUST NOT aceitar resposta de outro processo como boot bem sucedido; se
  a porta estiver ocupada e não puder ser mudada sem editar o código, MUST parar como falha
  externa com orientação de correção.
- **FR-030**: A skill MUST detectar e remover os artefatos de runtime gerados por cada execução
  da aplicação (exceto o ambiente isolado de dependências) e MUST NOT criar outros arquivos
  ignorados pelo git (ex.: `.env`); exemplos de configuração MUST ser versionáveis.
- **FR-031**: Arquivos de trabalho efêmeros da Fase 3 (plano de requisições, respostas,
  snapshots) MUST ficar em um diretório temporário do sistema operacional fora do repositório e
  MUST ser removidos ao final da execução, com sucesso ou falha.
- **FR-032**: Em caso de sucesso, a skill MUST imprimir o resumo `PHASE 3: REFACTORING COMPLETE`
  com a nova estrutura de diretórios e o resultado de cada verificação (boot, endpoints e
  `Zero anti-patterns remaining`).
- **FR-033**: Ao fim da Fase 3, com sucesso ou falha, a skill MUST gravar automaticamente
  `evidence/validation-project-N.md` na raiz do repositório (mesma resolução de `N` do
  relatório; reexecução sobrescreve), contendo: resultado da execução (limpa/FALHA), comando de
  boot usado, trecho da saída de boot, origem da linha de base de comportamento (execução real ou inferida do
  código), cada endpoint com status/formato antes e depois e o resultado da comparação,
  mudanças de contrato declaradas, resultado da reauditoria e, em caso de falha, o diagnóstico. A skill MUST informar o caminho
  gravado.

**Base de conhecimento**

- **FR-034**: Os arquivos de referência MUST cobrir as 5 áreas: análise de projeto (heurísticas
  de linguagem, framework, banco e arquitetura), catálogo de anti-patterns, template de
  relatório, guidelines de arquitetura MVC e playbook de refatoração.
- **FR-035**: O catálogo MUST conter ≥ 8 anti-patterns com ao menos um de cada severidade, cada
  um com identificador, severidade, sinais de detecção concretos, impacto e referência ao padrão
  de transformação; MUST incluir ao menos um anti-pattern de API deprecated.
- **FR-036**: A escala de severidade MUST reproduzir as definições do enunciado (CRITICAL, HIGH,
  MEDIUM, LOW baseadas em MVC e SOLID).
- **FR-037**: O playbook MUST conter ≥ 8 padrões de transformação, cada um com exemplo de código
  antes/depois; todo anti-pattern do catálogo MUST ter ao menos um padrão aplicável.
- **FR-038**: As guidelines MUST definir responsabilidades e proibições de cada camada, além de
  config, middlewares/error handling e entry point, com mapeamento de diretórios para ao menos
  Python e Node.js e critérios de adaptação para outras stacks.

**Scripts utilitários (opcionais)**

- **FR-039**: Se existirem, scripts MUST ficar apenas em `.claude/skills/refactor-arch/scripts/`,
  ser referenciados pelo `SKILL.md` com instrução de execução, argumentos e interpretação da
  saída; código de script MUST NOT estar embutido no Markdown da skill.
- **FR-040**: Scripts MUST ser genéricos e agnósticos de stack (valores dependentes do projeto
  recebidos por argumento ou detectados), depender apenas de ferramentas amplamente disponíveis,
  não instalar pacotes, tratar erros explicitamente, ser somente-leitura nas Fases 1–2 (exceto a
  gravação do relatório) e ter um procedimento manual equivalente descrito no `SKILL.md`.

**Portabilidade**

- **FR-041**: A skill MUST NOT conter, como regra ou instrução, identificadores específicos dos
  projetos-alvo (nomes de arquivos, rotas, tabelas, domínios).
- **FR-042**: A pasta da skill MUST ser idêntica nos 3 projetos, a partir da cópia canônica em
  `code-smells-project/`.

**Processo de iteração**

- **FR-043**: Toda execução com falha MUST ser seguida do ciclo reverter → atualizar a skill
  (somente na cópia canônica, de forma genérica) → commitar a alteração → re-sincronizar as
  cópias → reexecutar a partir da linha de base do código, repetido até uma execução limpa.
- **FR-044**: Reexecutar a skill após uma falha sem alteração do seu conteúdo MUST NOT ocorrer,
  exceto para falha comprovadamente externa à skill, registrada como tal.
- **FR-045**: Só uma execução limpa (todas as verificações da Fase 3 aprovadas na primeira
  validação, sem correções durante a execução) MUST ser aceita para commit; o código refatorado
  MUST NOT receber edições manuais.
- **FR-046**: Cada iteração MUST ser registrada com projeto, erro, causa, alteração feita na skill
  e versão da skill, e resumida na seção de desafios do README.

**Entregáveis**

- **FR-047**: O README da raiz MUST conter a Análise Manual: para cada projeto, ≥ 5 problemas
  (≥ 1 CRITICAL/HIGH, ≥ 2 MEDIUM, ≥ 2 LOW) com localização, severidade e justificativa.
- **FR-048**: O repositório entregue MUST conter exatamente `reports/audit-project-1.md`,
  `audit-project-2.md` e `audit-project-3.md` (gravados conforme FR-015) e exatamente
  `evidence/validation-project-1.md`, `-2.md` e `-3.md` (gravados conforme FR-033), todos das
  execuções aceitas.
- **FR-049**: O código refatorado de cada projeto (aceito conforme FR-045) MUST estar commitado
  com seu relatório e sua evidência; a linha de base do código MUST permanecer recuperável pelo
  histórico.
- **FR-050**: O README MUST conter as seções "Construção da Skill" (decisões de design,
  anti-patterns escolhidos e por quê, estratégia de agnosticismo, desafios e histórico de
  iterações), "Resultados" (findings por severidade por projeto, estrutura antes/depois,
  checklist de validação preenchido por projeto, referência aos arquivos de evidência em
  `evidence/`, observações por stack) e
  "Como Executar" (pré-requisitos, comandos por projeto, como validar).
- **FR-051**: Um documento de rastreabilidade MUST mapear cada requisito do enunciado ao
  artefato que o atende e à forma de verificação.

### Key Entities

- **Skill**: pacote `refactor-arch` composto pelo arquivo de orquestração, arquivos de referência
  e, opcionalmente, scripts utilitários; cada alteração gera uma nova versão identificável.
- **Arquivo de referência**: documento Markdown que fornece conhecimento de uma ou mais das 5
  áreas obrigatórias.
- **Anti-pattern**: entrada do catálogo com identificador, severidade, sinais de detecção,
  impacto e padrão de transformação associado.
- **Padrão de transformação**: entrada do playbook que descreve como eliminar um ou mais
  anti-patterns, com exemplo antes/depois.
- **Projeto-alvo**: codebase onde a skill é executada; possui stack, domínio, arquivos-fonte,
  entidades de dados e endpoints.
- **Linha de base do código**: conteúdo do projeto no commit `6d1ce62` (fora de `.claude/`),
  ponto de partida de toda execução avaliativa.
- **Ponto de restauração**: `HEAD` no momento da confirmação da Fase 3, para o qual a reversão
  retorna (equivale à linha de base do código enquanto o resultado refatorado não for commitado).
- **Linha de base de comportamento**: status e formato de resposta de cada endpoint inventariado,
  capturados da aplicação original no início da Fase 3 (ou inferidos do código, se o original
  não iniciar); referência para a comparação pós-refatoração.
- **Endpoint inventariado**: par método + path (com parâmetros e formato de resposta) registrado
  na Fase 1 e usado para validar a Fase 3.
- **Finding**: ocorrência de um anti-pattern em um projeto-alvo, com severidade, localização
  exata, descrição, impacto e recomendação.
- **Relatório de auditoria**: saída da Fase 2, composta por cabeçalho, resumo por severidade,
  findings ordenados e total; gravado pela skill em `reports/`.
- **Execução**: uma invocação da skill em um projeto, com resultado limpa ou falha, associada à
  versão da skill usada.
- **Registro de iteração**: entrada que liga uma execução com falha à causa e à alteração feita na
  skill antes da reexecução.
- **Problema da Análise Manual**: problema identificado pelo autor antes da skill, usado como
  referência de cobertura para a Fase 2.
- **Evidência de validação**: arquivo `evidence/validation-project-N.md` gravado pela skill ao fim
  da Fase 3, com resultado, boot, respostas dos endpoints, reauditoria e diagnóstico (se falha).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 3/3 projetos, o resumo da Fase 1 identifica corretamente linguagem, framework e
  domínio, e o número de arquivos-fonte informado é igual à contagem real.
- **SC-002**: Em 3/3 projetos, o relatório contém ≥ 5 findings e ≥ 1 finding CRITICAL ou HIGH.
- **SC-003**: 100% dos findings dos 3 relatórios apontam arquivo e linha(s) que existem e
  correspondem ao problema descrito, e 100% dos relatórios estão ordenados por severidade com
  contagens consistentes.
- **SC-004**: Em 3/3 projetos, ≥ 5 problemas da Análise Manual aparecem como findings.
- **SC-005**: Em 3/3 execuções, o relatório é gravado em `reports/` sem nenhuma ação manual e com
  conteúdo idêntico ao impresso, e o projeto não possui nenhuma alteração entre o início da skill
  e a resposta à pergunta de confirmação.
- **SC-006**: Em 3/3 projetos, a execução aceita é limpa: na primeira validação a aplicação
  inicia sem erros, 100% dos endpoints originais respondem com status e formato iguais à linha
  de base de comportamento (exceto mudanças de segurança declaradas) e a
  reauditoria encontra 0 anti-patterns (de 100% dos findings reportados, 100% eliminados).
- **SC-007**: 100% das execuções com falha terminam com diagnóstico e com o projeto revertível ao
  ponto de restauração sem perda de `.claude/`, `reports/` ou `evidence/`.
- **SC-008**: Em 3/3 projetos, existe `evidence/validation-project-N.md` gravado pela skill na
  execução aceita, sem ação manual, com 100% dos endpoints inventariados listados.
- **SC-009**: 100% das reexecuções após falha usam uma versão da skill diferente da execução que
  falhou (ou registram falha externa), conforme o registro de iterações.
- **SC-010**: O checklist de validação do enunciado (4 itens da Fase 1, 6 da Fase 2, 9 da Fase 3)
  está 100% atendido para cada um dos 3 projetos.
- **SC-011**: As 3 cópias da skill são idênticas, e a skill contém 0 identificadores específicos
  dos projetos-alvo em suas regras.
- **SC-012**: A base de conhecimento cobre 5/5 áreas, com ≥ 8 anti-patterns (4/4 severidades
  representadas, incluindo API deprecated) e ≥ 8 padrões de transformação, 100% com exemplo
  antes/depois e 100% dos anti-patterns ligados a ao menos um padrão.
- **SC-013**: O arquivo de orquestração tem menos de 500 linhas de corpo e descrição ≤ 1024
  caracteres.
- **SC-014**: Um avaliador sem contexto prévio localiza, em até 5 minutos, cada um dos
  entregáveis (Análise Manual, 3 relatórios, código refatorado, checklists, evidências,
  histórico de iterações, "Como Executar") e consegue reproduzir a validação de qualquer projeto
  seguindo apenas o README.
- **SC-015**: 100% dos requisitos do enunciado aparecem no documento de rastreabilidade com
  artefato e verificação associados.

## Assumptions

- A ferramenta é exclusivamente Claude Code; Gemini CLI e Codex estão fora de escopo.
- O ambiente de execução já possui os runtimes necessários aos projetos-alvo (Python 3 e
  Node.js, com seus gerenciadores de pacotes padrão), git e acesso de rede para instalar as
  dependências declaradas nos manifestos dos próprios projetos em ambientes isolados.
- Os banners e rótulos das saídas seguem o exemplo do enunciado (em inglês); descrições,
  impactos e recomendações dos findings são escritos em português.
- A refatoração acontece no próprio diretório do projeto-alvo, substituindo a estrutura original;
  a linha de base do código fica preservada no histórico git (commit `6d1ce62`) e serve de ponto
  de restauração para reexecuções.
- A pasta `reports/` fica na raiz do repositório git que contém os 3 projetos; os 3 projetos são
  executados na ordem 1 → 2 → 3 do enunciado, ou o número do relatório é passado como argumento.
- A reversão oferecida pela skill pede confirmação antes de descartar o código gerado, por ser
  uma ação destrutiva sobre a saída da execução.
- A Fase 3 NÃO DEVERIA adicionar dependências de terceiros; se uma for indispensável, ela é
  declarada no manifesto do projeto e citada no resumo da Fase 3.
- A validação de endpoints é feita por requisições HTTP locais; testes automatizados novos
  (suítes de teste) estão fora de escopo.
- São esperadas de 2 a 4 iterações da skill; cada reexecução avaliativa parte da linha de base do código.
- O ferramental Spec Kit (`.specify/`, `specs/`, skills `speckit-*`) não faz parte da skill nem
  é copiado para os projetos-alvo.
- A entrega final é um fork público no GitHub; publicar o repositório é uma ação do autor.

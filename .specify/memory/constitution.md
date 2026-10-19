<!--
Sync Impact Report
==================
Version change: 2.1.0 → 2.2.0
Bump rationale: MINOR — expansão material de regras do Princípio VII a partir do
/speckit-analyze (2026-10-19): permissão explícita e limitada para arquivos efêmeros em diretório
temporário do SO (antes implicitamente proibidos), novas regras de artefatos de runtime e de
verificação de porta, mensagem de bloqueio no lugar da pergunta quando não há ponto de
restauração, e glossário obrigatório para "linha de base". Nenhum princípio removido.

Modified principles:
- VII. Refatoração Segura e Comprovada — reversibilidade (bloqueio no lugar da pergunta; ponto de
  restauração = HEAD na confirmação; arquivos efêmeros em temp do SO); novas regras "Artefatos de
  runtime" e "Porta da aplicação"; texto da evidência com "linha de base de comportamento".

Added sections: nenhuma (novo item "Glossário obrigatório" em Restrições do Entregável).
Removed sections: nenhuma.
Modified sections: Restrições do Entregável ("Linha de base do código", glossário); Fluxo de
Trabalho e Quality Gates (etapa 4 e etapa 5.1/5.4 com "linha de base do código").

Templates/commands: não modificados (leem a constituição em tempo de execução).
Dependent artifacts: specs/001-refactor-arch-skill/{spec,plan,research,data-model,quickstart,
tasks}.md e contracts/ ✅ alinhados na mesma correção.
Follow-up TODOs: nenhum.
-->

# Constituição do Projeto refactor-arch (Desafio de Skills — MBA IA)

Este repositório **não** tem como produto final um sistema. O produto avaliado é a skill
`refactor-arch` (SKILL.md + arquivos de referência em Markdown), mais as evidências de que ela
funciona: código refatorado dos 3 projetos-alvo, relatórios de auditoria e o `README.md`
documentando o processo. Toda especificação, plano e tarefa gerados com Spec Kit DEVEM servir a
esse entregável e ser verificáveis contra o enunciado do desafio (`README.md` da raiz, versão do
commit inicial `6d1ce62`).

Convenção de linguagem normativa: **DEVE / NÃO DEVE** = obrigatório; **DEVERIA / NÃO DEVERIA** =
recomendado, desvio exige justificativa registrada no plano; **PODE** = opcional.

## Core Principles

### I. O Enunciado é a Fonte da Verdade

- Cada requisito, tarefa, restrição e critério de aceite do enunciado DEVE estar mapeado em uma
  matriz de rastreabilidade (requisito → artefato que o atende → forma de verificação). A matriz
  DEVE existir no plano da feature e ser revisada antes da entrega.
- Nomes, caminhos e formatos exigidos pelo enunciado são fixos e NÃO DEVEM ser alterados:
  nome da skill `refactor-arch`, arquivo `SKILL.md`, caminho `.claude/skills/refactor-arch/`,
  relatórios `reports/audit-project-{1,2,3}.md`, comando de invocação `/refactor-arch`.
- Os mínimos quantitativos do enunciado são pisos, não metas: ≥ 8 anti-patterns, ≥ 8 padrões de
  transformação, ≥ 5 findings por projeto, ≥ 1 CRITICAL/HIGH por projeto, ≥ 5 problemas manuais
  por projeto (≥ 1 CRITICAL/HIGH, ≥ 2 MEDIUM, ≥ 2 LOW).
- Em caso de ambiguidade no enunciado, DEVE prevalecer a interpretação mais estrita, e a
  decisão DEVE ser registrada (spec ou seção "Desafios" do README).
- Escopo extra (ferramentas, features, frameworks de teste, CI) NÃO DEVE ser adicionado se não
  contribuir diretamente para um requisito rastreado.

**Racional:** a avaliação é feita contra o enunciado; qualquer requisito não rastreado é um
ponto potencialmente perdido, e qualquer desvio de nome/caminho pode invalidar a correção.

### II. Anatomia de Skill Conforme a Anthropic

A skill DEVE seguir a documentação oficial de Skills do Claude Code e o guia de boas práticas de
autoria da Anthropic:

- `SKILL.md` DEVE iniciar com frontmatter YAML contendo `name: refactor-arch` (minúsculas, dígitos
  e hífens; ≤ 64 caracteres; igual ao nome do diretório) e `description` (≤ 1024 caracteres,
  em terceira pessoa, dizendo **o que** a skill faz **e quando** usá-la, com termos-gatilho como
  auditoria, anti-patterns, refatoração, MVC). Campos opcionais do frontmatter (ex.:
  `disable-model-invocation`, `allowed-tools`, `argument-hint`) só PODEM ser usados com
  justificativa registrada e NÃO DEVEM impedir a invocação via `/refactor-arch`.
- `SKILL.md` é um prompt de orquestração: DEVE descrever o fluxo das 3 fases, os critérios de
  saída de cada fase e QUANDO ler cada arquivo de referência. O conhecimento de domínio DEVE
  morar nos arquivos de referência (progressive disclosure). O corpo do `SKILL.md` DEVE ter
  menos de 500 linhas.
- Arquivos de referência DEVEM ser referenciados diretamente a partir do `SKILL.md` (um nível de
  profundidade, sem cadeias de referência), com caminhos relativos e barras `/`. Arquivos com
  mais de 100 linhas DEVEM começar com um sumário (table of contents).
- O texto DEVE ser conciso (assumir que o modelo já é competente; explicar apenas o que é
  específico desta tarefa), usar terminologia consistente (ex.: sempre "finding", "anti-pattern",
  "severidade", "camada") e NÃO DEVE conter informação sensível ao tempo.
- Fluxos multi-etapas DEVEM fornecer checklists que o agente copie e acompanhe, e laços de
  feedback explícitos (executar → validar → corrigir → revalidar).
- Para decisões frágeis (gate de confirmação, formato do relatório, validação) as instruções
  DEVEM ser prescritivas (baixa liberdade); para decisões dependentes de contexto (estrutura MVC
  exata de cada stack) DEVEM fornecer um padrão default e critérios de adaptação.

**Racional:** o enunciado exige "boas práticas de criação de skills"; a anatomia oficial garante
descoberta correta da skill, uso eficiente de contexto e comportamento previsível.

### III. Três Fases Sequenciais com Gate Humano (NÃO NEGOCIÁVEL)

- A skill DEVE executar exatamente três fases, em ordem, sem pular nem fundir fases:
  **Fase 1 — Análise** (detectar linguagem, framework, dependências, domínio, arquitetura,
  quantidade de arquivos-fonte e tabelas/entidades de dados; imprimir o resumo no formato de
  banner do enunciado `PHASE 1: PROJECT ANALYSIS`);
  **Fase 2 — Auditoria** (cruzar o código contra o catálogo, imprimir o relatório
  `ARCHITECTURE AUDIT REPORT` conforme o template);
  **Fase 3 — Refatoração** (capturar a linha de base de comportamento do original, reestruturar
  para MVC, validar, gravar a evidência e imprimir `PHASE 3: REFACTORING COMPLETE` com a nova
  estrutura e o resultado da validação).
- As Fases 1 e 2 DEVEM ser somente-leitura em relação ao projeto-alvo: nenhum arquivo do projeto
  pode ser criado, alterado, movido ou removido, e nenhum comando com efeito colateral sobre o
  projeto pode ser executado. **Única exceção:** ao final da Fase 2, antes da pergunta de
  confirmação, a skill DEVE gravar automaticamente o relatório de auditoria em `reports/` na raiz
  do repositório (Princípio VI). Nenhum passo manual é necessário para salvar o relatório.
- Ao final da Fase 2 a skill DEVE parar e pedir confirmação explícita
  (`Proceed with refactoring (Phase 3)? [y/n]`). Apenas uma resposta afirmativa explícita do
  usuário libera a Fase 3; qualquer outra resposta encerra a execução sem modificações.
- Uma execução que modifique arquivos antes da confirmação é considerada falha da skill,
  independentemente do resultado final.

**Racional:** o enunciado declara a confirmação obrigatória e a coloca no checklist; o humano
precisa revisar o relatório antes de qualquer mudança.

### IV. Agnosticismo de Tecnologia e Portabilidade

- `SKILL.md` e arquivos de referência NÃO DEVEM conter nomes de arquivos, rotas, tabelas,
  domínios ou identificadores específicos dos 3 projetos-alvo como instrução ou regra de
  detecção. Exemplos de código PODEM ilustrar stacks (Python/Flask, Node.js/Express e outras),
  desde que genéricos.
- A detecção de stack DEVE ser baseada em heurísticas (manifestos de dependência, extensões,
  imports, padrões de bootstrap, drivers de banco), cobrindo no mínimo Python e Node.js e
  descrevendo como generalizar para outras linguagens.
- A skill DEVE se adaptar ao nível de organização encontrado: em um monolito, criar as camadas;
  em um projeto parcialmente organizado, preservar o que já está adequado e corrigir apenas
  violações reais, propondo e executando as mudanças estruturais necessárias.
- A pasta `.claude/skills/refactor-arch/` DEVE ser idêntica (byte a byte) nos 3 projetos. A cópia
  canônica é a de `code-smells-project/`; as demais são cópias verificadas (ex.: `diff -r` sem
  diferenças) antes de cada execução e antes da entrega.
- A regra de agnosticismo vale também para os scripts em `scripts/` (ver Princípio V): um script
  que só funciona em uma stack ou em um projeto viola este princípio.
- Ajustes feitos para um projeto específico DEVEM ser generalizados no catálogo/playbook; uma
  skill que só funciona em um projeto é considerada acoplada e reprovada neste princípio.

**Racional:** o enunciado exige uma skill "agnóstica de tecnologia" e "copiável", validada em
duas stacks e em níveis de organização diferentes.

### V. Base de Conhecimento Completa e Acionável

- Os arquivos de referência DEVEM cobrir obrigatoriamente as 5 áreas de conhecimento, cada uma
  identificável por título: (1) Análise de projeto, (2) Catálogo de anti-patterns, (3) Template
  de relatório, (4) Guidelines de arquitetura MVC, (5) Playbook de refatoração.
- Todos os arquivos de referência (conhecimento de domínio) DEVEM ser Markdown. Scripts
  utilitários PODEM existir, desde que sigam as regras de scripts abaixo.
- **Regras de scripts:**
  - Scripts DEVEM ficar exclusivamente em `.claude/skills/refactor-arch/scripts/` e ser
    referenciados pelo `SKILL.md` por caminho relativo, com instrução explícita de **executar**
    (não ler/carregar no contexto), argumentos esperados e como interpretar a saída.
  - Código de script NÃO DEVE ser embutido no corpo Markdown da skill (`SKILL.md` e arquivos de
    referência). Exceção: os exemplos antes/depois do playbook e trechos ilustrativos de
    detecção, que são conhecimento e não automação.
  - Scripts DEVEM ser genéricos e agnósticos de stack: NÃO DEVEM conter caminhos, nomes de
    arquivos, portas, rotas, tabelas ou comandos específicos de um projeto-alvo ou de uma única
    linguagem/framework; todo valor dependente do projeto (diretório raiz, comando de boot,
    porta/URL base, lista de endpoints) DEVE ser recebido por argumento ou detectado em tempo de
    execução, e a lógica específica de stack DEVE ser tratada por detecção com ramos extensíveis.
  - Scripts DEVEM depender apenas de ferramentas amplamente disponíveis independentemente da stack
    do projeto-alvo (preferencialmente shell POSIX e utilitários padrão como `find`, `grep`,
    `curl`), declarar suas dependências no cabeçalho e NÃO DEVEM instalar pacotes (a instalação
    das dependências do projeto-alvo é responsabilidade do agente na Fase 3, conforme o
    Princípio VII).
  - Scripts DEVEM tratar erros explicitamente (mensagens claras e código de saída não zero),
    não usar constantes sem explicação e produzir saída estruturada e legível pelo agente.
  - Scripts usados nas Fases 1 e 2 DEVEM ser somente-leitura (Princípio III). Scripts da Fase 3
    que iniciem processos DEVEM encerrá-los ao final, inclusive em caso de falha.
  - A skill DEVE continuar executável se um script falhar: o `SKILL.md` DEVE descrever o
    procedimento manual equivalente para cada script.
- O catálogo DEVE conter ≥ 8 anti-patterns, com pelo menos um em cada severidade (CRITICAL, HIGH,
  MEDIUM, LOW), e DEVE incluir detecção de APIs deprecated com o equivalente moderno recomendado.
  Cada anti-pattern DEVE ter: identificador estável, severidade, sinais de detecção concretos e
  verificáveis (ex.: "query SQL concatenada com input do request", "query dentro de laço"),
  impacto e referência ao padrão de transformação correspondente no playbook.
- A escala de severidade DEVE reproduzir fielmente as definições do enunciado (CRITICAL, HIGH,
  MEDIUM, LOW baseadas em MVC e SOLID).
- O playbook DEVE conter ≥ 8 padrões de transformação, cada um com exemplo de código **antes** e
  **depois**, e cada anti-pattern do catálogo DEVE ter ao menos um padrão aplicável.
- As guidelines de arquitetura DEVEM definir responsabilidades e proibições de cada camada
  (Models, Views/Routes, Controllers), além de config, middlewares/error handling e entry point
  (composition root), com mapeamento de diretórios por stack.

**Racional:** o enunciado define as áreas e os mínimos; sinais vagos ("código ruim") não são
acionáveis para o agente.

### VI. Achados Rastreáveis e Verificáveis

- Todo finding DEVE conter severidade, nome do anti-pattern, arquivo e linha(s) exatos
  (`arquivo:linha` ou `arquivo:inicio-fim`), descrição, impacto e recomendação, no formato do
  template de relatório.
- Findings DEVEM ser ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW) e o relatório DEVE
  conter resumo por severidade e total, consistentes com a lista.
- A skill NÃO DEVE inventar findings: cada linha citada DEVE existir e corresponder ao problema
  descrito no código auditado. Findings duplicados para a mesma ocorrência NÃO DEVEM ser contados
  duas vezes.
- Em cada projeto, a Fase 2 DEVE encontrar ≥ 5 findings, ≥ 1 CRITICAL ou HIGH, e cobrir ≥ 5 dos
  problemas documentados na Análise Manual do README; APIs deprecated DEVEM ser reportadas quando
  presentes.
- A skill DEVE salvar automaticamente o relatório da Fase 2 em `reports/audit-project-N.md` na
  raiz do repositório git (criando `reports/` se não existir), com conteúdo idêntico ao impresso.
  O número `N` DEVE ser resolvido de forma genérica, nesta ordem: (1) argumento opcional da
  invocação; (2) relatório existente em `reports/` cujo cabeçalho `Project:` corresponda ao
  projeto atual (reexecução sobrescreve); (3) próximo número sequencial livre. A skill DEVE
  informar o caminho gravado. A invocação sem argumentos (`/refactor-arch`) DEVE continuar
  válida.

**Racional:** os itens do checklist de validação da Fase 2 dependem de precisão e ordenação; um
finding com linha errada não é verificável pelo avaliador.

### VII. Refatoração Segura e Comprovada (NÃO NEGOCIÁVEL)

- A Fase 3 DEVE produzir estrutura MVC explícita: módulo de config sem valores sensíveis
  hardcoded (segredos via variáveis de ambiente; defaults não sensíveis permitidos para boot
  local), Models abstraindo dados, Views/Routes apenas com roteamento/apresentação, Controllers
  concentrando o fluxo, error handling centralizado e entry point claro (composition root).
- O contrato externo DEVE ser preservado: mesmos métodos HTTP, paths, parâmetros, códigos de
  status e formato das respostas dos endpoints originais, exceto quando a mudança for a própria
  correção de um finding de segurança — nesse caso DEVE ser declarada no resumo da Fase 3 e na
  evidência.
- **Reversibilidade:** antes de alterar qualquer arquivo, a Fase 3 DEVE garantir um ponto de
  restauração: o projeto DEVE estar sob controle de versão git sem alterações pendentes fora de
  `.claude/` (verificado de forma somente-leitura nas Fases 1–2 e informado ao final da Fase 2).
  Se não houver ponto de restauração, a skill DEVE imprimir, no lugar da pergunta de
  confirmação, a mensagem de bloqueio com o motivo, NÃO DEVE iniciar a Fase 3 e DEVE orientar o
  usuário a commitar ou descartar as alterações. O ponto de restauração é o `HEAD` no momento da
  confirmação. A Fase 3 NÃO DEVE alterar `.claude/` (incluindo a própria skill) nem `reports/`;
  fora do diretório do projeto, a única escrita persistente permitida é o arquivo de evidência em
  `evidence/`. Arquivos de trabalho efêmeros (plano de requisições, respostas, snapshots) PODEM
  ser criados apenas em um diretório temporário do sistema operacional fora do repositório
  (ex.: criado com `mktemp -d`) e DEVEM ser removidos ao final da execução, com sucesso ou falha.
- **Artefatos de runtime:** arquivos gerados pela execução da aplicação durante a captura da linha
  de base de comportamento ou a validação (ex.: bancos locais, caches) DEVEM ser detectados e
  removidos após cada execução da aplicação, exceto o ambiente isolado de dependências. A Fase 3
  NÃO DEVE criar outros arquivos ignorados pelo git (ex.: `.env`); exemplos de configuração DEVEM
  ser versionáveis (ex.: `.env.example`).
- **Porta da aplicação:** antes de iniciar a aplicação (original ou refatorada), a skill DEVE
  verificar que a porta usada está livre. Respostas de outro processo NUNCA contam como boot bem
  sucedido. Se a porta estiver ocupada e não houver forma de mudar a porta sem editar o código
  (ex.: variável de ambiente já suportada pela aplicação ou opção de linha de comando do
  framework), a execução DEVE parar como falha externa, com orientação de correção.
- **Ambiente isolado de dependências:** a Fase 3 DEVE instalar as dependências declaradas no
  manifesto do projeto somente em um ambiente isolado dentro do diretório do projeto, pelo
  mecanismo padrão da stack (ex.: ambiente virtual em Python, pasta local de dependências em
  Node.js), cujo caminho DEVE ser ignorado pelo git. NÃO DEVE instalar no ambiente global ou do
  usuário. O ambiente isolado DEVE ser reutilizado quando existir e preservado pela reversão.
- **Linha de base de comportamento:** no início da Fase 3, após a confirmação e antes de
  qualquer modificação, a skill DEVE subir a aplicação original seguindo seus passos de execução
  documentados, exercitar todos os endpoints inventariados, registrar status e formato
  (estrutura/campos) de cada resposta, encerrar a aplicação e remover os artefatos gerados por
  essa execução. Se o original não iniciar, a referência DEVE ser o comportamento inferido do
  código, marcado como "inferida" na evidência. Valores voláteis (ids gerados, timestamps,
  ordem) NÃO entram na comparação.
- A Fase 3 DEVE validar: (a) a aplicação inicia sem erros com o comando de execução da stack;
  (b) todos os endpoints originais (inventariados na Fase 1) são exercitados e respondem com
  status e formato iguais à linha de base de comportamento — divergência não declarada como
  correção de segurança é falha; (c) uma reauditoria do código refatorado contra o catálogo
  retorna **zero anti-patterns de qualquer severidade** (CRITICAL a LOW) — qualquer finding
  remanescente é falha.
- **Falha é falha da skill:** se a validação falhar, a skill NÃO DEVE remendar o código gerado
  para fazê-lo passar. Ela DEVE parar, declarar a execução como **FALHA**, imprimir o
  diagnóstico (erro observado, transformação/arquivo de referência que o originou e a lacuna
  provável na skill) e oferecer a reversão do projeto ao ponto de restauração, restrita ao
  diretório do projeto e preservando `.claude/`, `reports/`, `evidence/` e o ambiente isolado
  de dependências. A skill NÃO DEVE declarar sucesso
  sem evidência da validação.
- **Execução limpa:** só é aceita (para commit e para os gates) a execução cuja Fase 3 passe em
  todas as verificações na primeira validação, sem correções durante a execução.
- Processos iniciados para validação (servidores) DEVEM ser encerrados ao final.
- **Evidência gravada pela skill:** ao fim da Fase 3, com sucesso ou falha, a skill DEVE gravar
  automaticamente `evidence/validation-project-N.md` na raiz do repositório (mesma resolução de
  `N` do relatório; reexecução sobrescreve), contendo: resultado (limpa/FALHA), comando de boot,
  trecho da saída de boot, origem da linha de base de comportamento (real/inferida), cada
  endpoint com
  status/formato antes e depois e o resultado da comparação, mudanças de contrato declaradas,
  resultado da reauditoria e, se falha, o diagnóstico. Nenhum passo manual é necessário; a seção
  "Resultados" do README DEVE referenciar esses arquivos.

**Racional:** o critério de aceite "aplicação funciona após refatoração" é obrigatório em 3/3
projetos; refatoração sem validação não tem valor para a avaliação.

## Restrições do Entregável

- **Ferramenta:** exclusivamente Claude Code com Custom Skills. Gemini CLI e Codex não fazem
  parte deste projeto.
- **Localização da skill:** `code-smells-project/.claude/skills/refactor-arch/`,
  `ecommerce-api-legacy/.claude/skills/refactor-arch/` e
  `task-manager-api/.claude/skills/refactor-arch/`. A skill NÃO DEVE ser instalada em
  `.claude/skills/` da raiz, reservada às skills de ferramental (Spec Kit).
- **Projetos-alvo:** `code-smells-project/` (Python/Flask, e-commerce), `ecommerce-api-legacy/`
  (Node.js/Express, LMS com checkout) e `task-manager-api/` (Python/Flask, parcialmente
  organizado). O código refatorado de cada um DEVE ser commitado no repositório.
- **Relatórios:** exatamente 3 arquivos em `reports/` na raiz:
  `audit-project-1.md`, `audit-project-2.md`, `audit-project-3.md`.
- **Evidências:** exatamente 3 arquivos em `evidence/` na raiz, gravados pela skill nas execuções
  aceitas: `validation-project-1.md`, `validation-project-2.md`, `validation-project-3.md`.
- **README.md da raiz** DEVE conter as seções: (A) "Análise Manual" — problemas por projeto, com
  severidade e justificativa; (B) "Construção da Skill" — decisões de design, anti-patterns
  escolhidos e por quê, estratégia de agnosticismo, desafios e soluções; (C) "Resultados" —
  findings por severidade por projeto, estrutura antes/depois, checklist de validação preenchido
  por projeto, referência às evidências em `evidence/` e observações por stack; (D) "Como Executar" — pré-requisitos,
  comandos por projeto e como validar a refatoração.
- **Ferramental Spec Kit** (`.specify/`, `specs/`, skills `speckit-*`) é apoio ao processo e NÃO
  DEVE ser copiado para dentro dos projetos-alvo nem referenciado pela skill.
- **Linha de base do código:** o estado original dos projetos (commit inicial `6d1ce62`) DEVE
  permanecer recuperável via git para reexecuções e para a comparação antes/depois.
- **Glossário obrigatório:** "linha de base do código" = conteúdo do projeto no commit `6d1ce62`
  (fora de `.claude/`); "ponto de restauração" = `HEAD` no momento da confirmação da Fase 3
  (equivale à linha de base do código enquanto o resultado refatorado não for commitado);
  "linha de base de comportamento" = status e formato das respostas do original capturados no
  início da Fase 3. O termo "linha de base" sozinho NÃO DEVE ser usado.
- **Entrega final:** repositório público no GitHub (fork do repositório base). Segredos reais e
  arquivos ignorados pelo `.gitignore` (`.env`, `node_modules/`, `*.db`, ambientes virtuais) NÃO
  DEVEM ser commitados.

## Fluxo de Trabalho e Quality Gates

Ordem obrigatória (espelha a ordem sugerida no enunciado):

1. **Análise Manual** dos 3 projetos → seção A do README. *Gate G1:* ≥ 5 problemas por projeto
   com a distribuição mínima de severidades, cada um com arquivo/linha e justificativa.
2. **Construção da Skill** na cópia canônica. *Gate G2 (estático):* frontmatter válido; corpo do
   `SKILL.md` < 500 linhas; referências a um nível; 5 áreas cobertas; ≥ 8 anti-patterns com as 4
   severidades e APIs deprecated; ≥ 8 transformações com antes/depois; nenhum identificador
   específico dos projetos-alvo nas regras; nenhum código de script embutido no Markdown;
   scripts (se houver) apenas em `scripts/`, parametrizados, sem valores específicos de projeto
   ou stack, e testados nas duas stacks (Python e Node.js).
3. **Sincronização** da skill para os outros 2 projetos. *Gate G3:* `diff -r` sem diferenças.
4. **Execução** de `/refactor-arch` em cada projeto, a partir da linha de base do código. *Gate G4
   (por projeto):* execução limpa; checklist de validação do enunciado (Fases 1, 2 e 3)
   integralmente marcado; reauditoria com zero anti-patterns; relatório gravado pela skill em
   `reports/` e evidência gravada em `evidence/`; código refatorado commitado.
5. **Iteração** (esperadas 2–4 rodadas), ciclo obrigatório **reverter → atualizar a skill →
   reexecutar**, repetido até uma execução limpa:
   1. Reverter o projeto ao ponto de restauração (linha de base do código), preservando `.claude/`,
      `reports/`, `evidence/` e o ambiente isolado de dependências.
   2. Diagnosticar a causa e corrigir a skill **somente** na cópia canônica, de forma genérica
      (catálogo, playbook, guidelines, `SKILL.md` ou scripts).
   3. Commitar a alteração da skill e voltar ao Gate G3 (sincronizar as cópias).
   4. Reexecutar a skill a partir da linha de base do código em todos os projetos afetados.

   É **proibido** reexecutar a skill após uma falha sem que seu conteúdo tenha mudado (a versão
   da skill — commit/hash da pasta — DEVE ser diferente da execução que falhou). Única exceção:
   falha comprovadamente externa à skill (ex.: porta ocupada, runtime ausente), registrada como
   tal. Correções manuais no código refatorado para "passar" no gate NÃO são permitidas; o
   resultado commitado DEVE ser saída de uma execução limpa. Cada iteração DEVE ser registrada
   (projeto, erro, causa, alteração feita na skill, versão da skill) e resumida na seção
   "Desafios" do README.
6. **Documentação final** — seções B, C e D do README. *Gate G5 (aceite):* critérios de aceite
   do enunciado atendidos em **3/3 projetos** — Fase 1 detecta a stack; Fase 2 com ≥ 5 findings
   e ≥ 1 CRITICAL/HIGH; Fase 3 com aplicação funcionando — e matriz de rastreabilidade 100%
   verificada.

Commits DEVEM seguir Conventional Commits e ser granulares por etapa (ex.: `docs:` análise
manual, `feat(skill):` skill, `refactor(project-1):` saída da Fase 3, `docs(reports):`
relatórios).

## Governance

- Esta constituição prevalece sobre qualquer outra prática, spec, plano ou tarefa do repositório.
  O enunciado do desafio (`README.md` no commit `6d1ce62`) prevalece sobre esta constituição; em
  conflito, a constituição DEVE ser emendada para se alinhar ao enunciado.
- Todo `plan.md` gerado por `/speckit-plan` DEVE incluir um "Constitution Check" avaliando os
  princípios I–VII e os gates aplicáveis; violações DEVEM ser justificadas em "Complexity
  Tracking" ou corrigidas antes de seguir. `/speckit-analyze` DEVE ser executado antes de
  `/speckit-implement` para verificar consistência entre spec, plano, tarefas e esta constituição.
- Emendas DEVEM ser feitas via `/speckit-constitution`, com Sync Impact Report, justificativa e
  atualização de versão por SemVer: **MAJOR** para remoção ou redefinição incompatível de
  princípio/gate; **MINOR** para novo princípio, seção ou expansão material de regra; **PATCH**
  para esclarecimentos e correções de redação.
- Revisão de conformidade obrigatória: ao fim de cada gate (G1–G5) e imediatamente antes da
  entrega final, verificando cada regra DEVE/NÃO DEVE desta constituição e o checklist de
  validação do enunciado para os 3 projetos.

**Version**: 2.2.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19

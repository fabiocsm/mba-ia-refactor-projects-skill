# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# Entrega do Desafio

> As seções abaixo documentam a solução. O texto acima é o enunciado original (commit `6d1ce62`),
> preservado sem alterações.

## Análise Manual

Problemas identificados manualmente, antes da criação da skill, lendo o código dos 3 projetos na
linha de base do código (commit `6d1ce62`). As localizações `arquivo:linha` são relativas ao
diretório de cada projeto. A coluna **Finding da skill (matched_by)** relaciona cada problema ao
finding correspondente no relatório gerado pela skill (`reports/audit-project-N.md`).

### Projeto 1 — code-smells-project (Python/Flask)

| # | Severidade | Problema | Arquivo:linha | Justificativa | Finding da skill (matched_by) |
|---|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection por concatenação de strings | `models.py:28`, `models.py:47-50`, `models.py:58-60`, `models.py:110`, `models.py:291` | Valores vindos do request (inclusive e-mail/senha do login e termo de busca) são concatenados no SQL; permite bypass de login e leitura/alteração arbitrária do banco. | |
| 2 | CRITICAL | Credenciais/segredos hardcoded | `app.py:7`, `controllers.py:289` | `SECRET_KEY` fixa no código e versionada; qualquer pessoa com acesso ao repositório pode forjar sessões. | |
| 3 | CRITICAL | Endpoints administrativos sem proteção | `app.py:47-57`, `app.py:59-78` | `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL arbitrário enviado no corpo, ambos sem autenticação. | |
| 4 | CRITICAL | God file: acesso a dados + regra de negócio + formatação de 3 domínios | `models.py:1-314` | Produtos, usuários e pedidos (queries, cálculo de desconto, baixa de estoque, montagem de dicionários) no mesmo módulo; impossível testar ou alterar um domínio isoladamente. | |
| 5 | CRITICAL | Senhas armazenadas e comparadas em texto puro | `database.py:76-78`, `models.py:109-111`, `models.py:126-129` | Senhas gravadas sem hash e comparadas direto no SQL; vazamento do banco expõe todas as credenciais. | |
| 6 | HIGH | Exposição de dados sensíveis nas respostas | `models.py:83`, `models.py:99`, `controllers.py:285-289` | `GET /usuarios` devolve o campo `senha`; `/health` devolve `secret_key`, `db_path` e flag de debug. | |
| 7 | HIGH | Modo debug e bind amplo ativos por padrão | `app.py:8`, `app.py:88` | `debug=True` com `host="0.0.0.0"` expõe o debugger interativo (execução de código) na rede. | |
| 8 | HIGH | Estado global mutável compartilhado | `database.py:4-10` | Conexão única global com `check_same_thread=False` compartilhada por todas as requisições; acoplamento e condições de corrida. | |
| 9 | MEDIUM | N+1 queries (query dentro de laço) | `models.py:187-193`, `models.py:219-225` | Para cada pedido uma query de itens e, para cada item, outra de produto; custo cresce linearmente com o volume. | |
| 10 | MEDIUM | Código duplicado | `controllers.py:26-50`, `controllers.py:66-90`, `models.py:12-21`, `models.py:31-40`, `models.py:304-313` | Validação de produto e mapeamento linha→dicionário copiados; correções precisam ser replicadas e divergem (o update não valida o nome). | |
| 11 | MEDIUM | Tratamento de erros genérico e espalhado | `controllers.py:10-12`, `controllers.py:21-22`, `controllers.py:185-186` | Cada handler captura `Exception` e devolve `str(e)` com 500, vazando detalhes internos; não há handler centralizado. | |
| 12 | LOW | `print` no lugar de logger | `controllers.py:8`, `controllers.py:57`, `controllers.py:208-210` | Sem níveis nem destino configurável; mensagens de "envio" de e-mail/SMS simuladas via `print`. | |
| 13 | LOW | Magic numbers na regra de desconto | `models.py:257-262` | Faixas `10000/5000/1000` e taxas `0.1/0.05/0.02` sem nome; regra de negócio opaca. | |
| 14 | LOW | Imports não utilizados | `models.py:2`, `database.py:2` | `sqlite3` em `models.py` e `os` em `database.py` nunca são usados; ruído e acoplamento aparente. | |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

| # | Severidade | Problema | Arquivo:linha | Justificativa | Finding da skill (matched_by) |
|---|---|---|---|---|---|
| 1 | CRITICAL | Credenciais/segredos hardcoded | `src/utils.js:1-7` | Senha do banco e chave do gateway de pagamento (`pk_live_…`) versionadas no código. | |
| 2 | CRITICAL | God class: banco, schema, seed, rotas e regra de negócio na mesma classe | `src/AppManager.js:4-139` | `AppManager` cria o banco, define tabelas, popula dados, registra rotas e implementa checkout e relatório; nenhuma separação de camadas. | |
| 3 | CRITICAL | Hash de senha fraco/caseiro | `src/utils.js:17-23`, `src/AppManager.js:68` | `badCrypto` é base64 truncado (reversível e sem salt) e usa senha padrão `123456` quando ausente. | |
| 4 | CRITICAL | Endpoints administrativos sem proteção | `src/AppManager.js:80`, `src/AppManager.js:131` | Relatório financeiro e exclusão de usuários acessíveis sem autenticação/autorização. | |
| 5 | HIGH | Dados sensíveis em logs | `src/AppManager.js:45` | Número completo do cartão e chave do gateway impressos no console a cada checkout. | |
| 6 | HIGH | Regra de negócio dentro do handler da rota | `src/AppManager.js:28-78` | Aprovação de pagamento, criação de usuário, matrícula e auditoria implementadas no callback da rota. | |
| 7 | HIGH | Estado global mutável | `src/utils.js:9-15` | `globalCache` e `totalRevenue` exportados e mutados por qualquer módulo; cache sem limite nem dono. | |
| 8 | MEDIUM | Callback hell | `src/AppManager.js:37-77`, `src/AppManager.js:83-128` | Até 5 níveis de callbacks aninhados; fluxo e tratamento de erros difíceis de seguir e testar. | |
| 9 | MEDIUM | N+1 queries | `src/AppManager.js:92`, `src/AppManager.js:104-106` | Uma query de matrículas por curso e duas por matrícula (usuário e pagamento). | |
| 10 | MEDIUM | Erros ignorados / tratamento inconsistente | `src/AppManager.js:92-93`, `src/AppManager.js:133-135` | O `err` dos callbacks é ignorado (acesso a `enrollments.length` com `undefined` derruba o processo); delete responde sucesso mesmo em erro. | |
| 11 | MEDIUM | Validação de entrada ausente | `src/AppManager.js:35`, `src/AppManager.js:132` | Só checa presença de campos; formato de e-mail, cartão e id não são validados. | |
| 12 | LOW | Nomes pobres/abreviados | `src/AppManager.js:29-33` | `u`, `e`, `p`, `cid`, `cc` escondem o significado dos dados. | |
| 13 | LOW | `console.log` no lugar de logger | `src/utils.js:13`, `src/app.js:13` | Logs sem nível nem destino configurável. | |
| 14 | LOW | Código morto e imports não usados | `src/AppManager.js:2`, `src/utils.js:10` | `totalRevenue` é importado e exportado mas nunca usado/atualizado. | |
| 15 | LOW | Magic numbers/strings | `src/utils.js:19`, `src/AppManager.js:46` | Laço de `10000` iterações e regra "cartão começando com `4`" sem nome. | |

### Projeto 3 — task-manager-api (Python/Flask)

| # | Severidade | Problema | Arquivo:linha | Justificativa | Finding da skill (matched_by) |
|---|---|---|---|---|---|
| 1 | CRITICAL | Credenciais/segredos hardcoded | `app.py:13`, `services/notification_service.py:7-10` | `SECRET_KEY` e usuário/senha SMTP versionados no código. | |
| 2 | CRITICAL | Hash de senha fraco (MD5 sem salt) | `models/user.py:27-32` | MD5 é quebrável por força bruta/rainbow tables; não é algoritmo de senha. | |
| 3 | HIGH | Exposição de dados sensíveis nas respostas | `models/user.py:16-25`, `routes/user_routes.py:85`, `routes/user_routes.py:209` | `to_dict()` inclui o hash da senha, devolvido no cadastro, atualização e login. | |
| 4 | HIGH | Regra de negócio nas rotas (camada de controller ausente) | `routes/report_routes.py:12-101`, `routes/task_routes.py:85-154` | Cálculo de relatórios, validações e criação de entidades direto nos handlers, apesar de existirem `models/` e `services/`. | |
| 5 | HIGH | Modo debug e bind amplo ativos por padrão | `app.py:34` | `debug=True` com `host='0.0.0.0'` expõe o debugger interativo na rede. | |
| 6 | MEDIUM | N+1 queries | `routes/task_routes.py:41-51`, `routes/report_routes.py:55-56`, `routes/report_routes.py:161-163` | Para cada task busca usuário e categoria; para cada usuário/categoria uma nova contagem. | |
| 7 | MEDIUM | APIs deprecated | `models/task.py:15-16`, `routes/task_routes.py:31`, `routes/user_routes.py:29` | `datetime.utcnow()` é obsoleto desde Python 3.12 (usar `datetime.now(timezone.utc)`); `Query.get()` é API legada do SQLAlchemy 2.x (usar `db.session.get()`). | |
| 8 | MEDIUM | Código duplicado | `routes/task_routes.py:30-39`, `routes/task_routes.py:71-80`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-37` | Cálculo de "atrasada" repetido em 4 lugares enquanto `Task.is_overdue()` (`models/task.py:50-60`) não é usado. | |
| 9 | MEDIUM | Tratamento de erros genérico (`except:` nu) | `routes/task_routes.py:62`, `routes/task_routes.py:137`, `routes/report_routes.py:186` | Captura tudo (inclusive `KeyboardInterrupt`) e esconde a causa; sem handler centralizado. | |
| 10 | MEDIUM | Validação de entrada ausente | `routes/report_routes.py:196-202`, `routes/task_routes.py:113` | `PUT /categories/<id>` não verifica corpo nulo; prioridade não numérica causa `TypeError` (500). | |
| 11 | LOW | Imports não utilizados | `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:3-7` | `os`, `sys`, `json`, `time`, `math`, `hashlib` importados sem uso. | |
| 12 | LOW | `print` no lugar de logger | `routes/task_routes.py:149`, `routes/user_routes.py:83`, `utils/helpers.py:39` | Logs sem nível nem destino configurável. | |
| 13 | LOW | Magic numbers ignorando constantes existentes | `routes/task_routes.py:96-114`, `routes/user_routes.py:64` | Limites `3`, `200`, `1..5` e `4` repetidos enquanto `utils/helpers.py:110-116` define as constantes. | |
| 14 | LOW | Nomes pobres | `routes/report_routes.py:24-28` | `p1`…`p5` escondem a semântica de prioridade. | |

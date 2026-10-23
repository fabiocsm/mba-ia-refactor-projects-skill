> **Entrega:** [Análise Manual](#análise-manual) · [Construção da Skill](#construção-da-skill) ·
> [Resultados](#resultados) · [Como Executar](#como-executar) · Skill em
> `*/.claude/skills/refactor-arch/` · Relatórios em [`reports/`](reports/) · Evidências em
> [`evidence/`](evidence/) · Histórico de iterações em [`docs/iteration-log.md`](docs/iteration-log.md).
> O texto a seguir, até "Entrega do Desafio", é o enunciado original.

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
| 1 | CRITICAL | SQL Injection por concatenação de strings | `models.py:28`, `models.py:47-50`, `models.py:58-60`, `models.py:110`, `models.py:291` | Valores vindos do request (inclusive e-mail/senha do login e termo de busca) são concatenados no SQL; permite bypass de login e leitura/alteração arbitrária do banco. | AP-02 (`models.py:28`, …) |
| 2 | CRITICAL | Credenciais/segredos hardcoded | `app.py:7`, `controllers.py:289` | `SECRET_KEY` fixa no código e versionada; qualquer pessoa com acesso ao repositório pode forjar sessões. | AP-01 (`app.py:7`); `controllers.py:289` em AP-09 |
| 3 | CRITICAL | Endpoints administrativos sem proteção | `app.py:47-57`, `app.py:59-78` | `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL arbitrário enviado no corpo, ambos sem autenticação. | AP-04 (`app.py:47-57`, `app.py:59-78`) |
| 4 | CRITICAL | God file: acesso a dados + regra de negócio + formatação de 3 domínios | `models.py:1-314` | Produtos, usuários e pedidos (queries, cálculo de desconto, baixa de estoque, montagem de dicionários) no mesmo módulo; impossível testar ou alterar um domínio isoladamente. | AP-03 (`models.py:133-169`, `models.py:235-273`) |
| 5 | CRITICAL | Senhas armazenadas e comparadas em texto puro | `database.py:76-78`, `models.py:109-111`, `models.py:126-129` | Senhas gravadas sem hash e comparadas direto no SQL; vazamento do banco expõe todas as credenciais. | AP-05 (`database.py:76-79`, `models.py:109-111`) |
| 6 | HIGH | Exposição de dados sensíveis nas respostas | `models.py:83`, `models.py:99`, `controllers.py:285-289` | `GET /usuarios` devolve o campo `senha`; `/health` devolve `secret_key`, `db_path` e flag de debug. | AP-09 (`models.py:72-87`, `controllers.py:276-290`) |
| 7 | HIGH | Modo debug e bind amplo ativos por padrão | `app.py:8`, `app.py:88` | `debug=True` com `host="0.0.0.0"` expõe o debugger interativo (execução de código) na rede. | AP-10 (`app.py:8`, `app.py:88`) |
| 8 | HIGH | Estado global mutável compartilhado | `database.py:4-10` | Conexão única global com `check_same_thread=False` compartilhada por todas as requisições; acoplamento e condições de corrida. | AP-07 (`database.py:4`, `database.py:8-10`) |
| 9 | MEDIUM | N+1 queries (query dentro de laço) | `models.py:187-193`, `models.py:219-225` | Para cada pedido uma query de itens e, para cada item, outra de produto; custo cresce linearmente com o volume. | AP-11 (`models.py:188`, `models.py:220`) |
| 10 | MEDIUM | Código duplicado | `controllers.py:26-50`, `controllers.py:66-90`, `models.py:12-21`, `models.py:31-40`, `models.py:304-313` | Validação de produto e mapeamento linha→dicionário copiados; correções precisam ser replicadas e divergem (o update não valida o nome). | AP-14 (`models.py:12-21`, `controllers.py:28-54`) |
| 11 | MEDIUM | Tratamento de erros genérico e espalhado | `controllers.py:10-12`, `controllers.py:21-22`, `controllers.py:185-186` | Cada handler captura `Exception` e devolve `str(e)` com 500, vazando detalhes internos; não há handler centralizado. | AP-13 (`controllers.py:10-12`, …) |
| 12 | LOW | `print` no lugar de logger | `controllers.py:8`, `controllers.py:57`, `controllers.py:208-210` | Sem níveis nem destino configurável; mensagens de "envio" de e-mail/SMS simuladas via `print`. | AP-19 (`controllers.py:8`, …) |
| 13 | LOW | Magic numbers na regra de desconto | `models.py:257-262` | Faixas `10000/5000/1000` e taxas `0.1/0.05/0.02` sem nome; regra de negócio opaca. | AP-17 (`models.py:257-262`) |
| 14 | LOW | Imports não utilizados | `models.py:2`, `database.py:2` | `sqlite3` em `models.py` e `os` em `database.py` nunca são usados; ruído e acoplamento aparente. | AP-20 (`models.py:2`, `database.py:2`) |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

| # | Severidade | Problema | Arquivo:linha | Justificativa | Finding da skill (matched_by) |
|---|---|---|---|---|---|
| 1 | CRITICAL | Credenciais/segredos hardcoded | `src/utils.js:1-7` | Senha do banco e chave do gateway de pagamento (`pk_live_…`) versionadas no código. | AP-01 (`src/utils.js:3`, `src/utils.js:4`) |
| 2 | CRITICAL | God class: banco, schema, seed, rotas e regra de negócio na mesma classe | `src/AppManager.js:4-139` | `AppManager` cria o banco, define tabelas, popula dados, registra rotas e implementa checkout e relatório; nenhuma separação de camadas. | AP-03 (`src/AppManager.js:4-141`) |
| 3 | CRITICAL | Hash de senha fraco/caseiro | `src/utils.js:17-23`, `src/AppManager.js:68` | `badCrypto` é base64 truncado (reversível e sem salt) e usa senha padrão `123456` quando ausente. | AP-05 (`src/utils.js:17-23`, `src/AppManager.js:68`) |
| 4 | CRITICAL | Endpoints administrativos sem proteção | `src/AppManager.js:80`, `src/AppManager.js:131` | Relatório financeiro e exclusão de usuários acessíveis sem autenticação/autorização. | AP-04 (`src/AppManager.js:80`) |
| 5 | HIGH | Dados sensíveis em logs | `src/AppManager.js:45` | Número completo do cartão e chave do gateway impressos no console a cada checkout. | AP-09 (`src/AppManager.js:45`) |
| 6 | HIGH | Regra de negócio dentro do handler da rota | `src/AppManager.js:28-78` | Aprovação de pagamento, criação de usuário, matrícula e auditoria implementadas no callback da rota. | AP-03 (mesmas linhas; regra de desempate AP-03 > AP-06) |
| 7 | HIGH | Estado global mutável | `src/utils.js:9-15` | `globalCache` e `totalRevenue` exportados e mutados por qualquer módulo; cache sem limite nem dono. | AP-07 (`src/utils.js:9-10`) |
| 8 | MEDIUM | Callback hell | `src/AppManager.js:37-77`, `src/AppManager.js:83-128` | Até 5 níveis de callbacks aninhados; fluxo e tratamento de erros difíceis de seguir e testar. | AP-16 (`src/AppManager.js:25-78`, `src/AppManager.js:83-128`) |
| 9 | MEDIUM | N+1 queries | `src/AppManager.js:92`, `src/AppManager.js:104-106` | Uma query de matrículas por curso e duas por matrícula (usuário e pagamento). | AP-11 (`src/AppManager.js:92`, `:104`, `:106`) |
| 10 | MEDIUM | Erros ignorados / tratamento inconsistente | `src/AppManager.js:92-93`, `src/AppManager.js:133-135` | O `err` dos callbacks é ignorado (acesso a `enrollments.length` com `undefined` derruba o processo); delete responde sucesso mesmo em erro. | AP-13 (`src/AppManager.js:92`, `src/AppManager.js:133`) |
| 11 | MEDIUM | Validação de entrada ausente | `src/AppManager.js:35`, `src/AppManager.js:132` | Só checa presença de campos; formato de e-mail, cartão e id não são validados. | AP-12 (`src/AppManager.js:29-35`) |
| 12 | LOW | Nomes pobres/abreviados | `src/AppManager.js:29-33` | `u`, `e`, `p`, `cid`, `cc` escondem o significado dos dados. | AP-18 (`src/AppManager.js:29-33`) |
| 13 | LOW | `console.log` no lugar de logger | `src/utils.js:13`, `src/app.js:13` | Logs sem nível nem destino configurável. | AP-19 (`src/app.js:13`, `src/utils.js:13`) |
| 14 | LOW | Código morto e imports não usados | `src/AppManager.js:2`, `src/utils.js:10` | `totalRevenue` é importado e exportado mas nunca usado/atualizado. | AP-20 (`src/AppManager.js:2`, `src/utils.js:10`) |
| 15 | LOW | Magic numbers/strings | `src/utils.js:19`, `src/AppManager.js:46` | Laço de `10000` iterações e regra "cartão começando com `4`" sem nome. | AP-17 (`src/AppManager.js:46`, `src/utils.js:19-20`) |

### Projeto 3 — task-manager-api (Python/Flask)

| # | Severidade | Problema | Arquivo:linha | Justificativa | Finding da skill (matched_by) |
|---|---|---|---|---|---|
| 1 | CRITICAL | Credenciais/segredos hardcoded | `app.py:13`, `services/notification_service.py:7-10` | `SECRET_KEY` e usuário/senha SMTP versionados no código. | AP-01 (`app.py:13`, `services/notification_service.py:9-10`) |
| 2 | CRITICAL | Hash de senha fraco (MD5 sem salt) | `models/user.py:27-32` | MD5 é quebrável por força bruta/rainbow tables; não é algoritmo de senha. | AP-05 (`models/user.py:29`, `models/user.py:32`) |
| 3 | HIGH | Exposição de dados sensíveis nas respostas | `models/user.py:16-25`, `routes/user_routes.py:85`, `routes/user_routes.py:209` | `to_dict()` inclui o hash da senha, devolvido no cadastro, atualização e login. | AP-09 (`models/user.py:16-25`, `routes/user_routes.py:85`) |
| 4 | HIGH | Regra de negócio nas rotas (camada de controller ausente) | `routes/report_routes.py:12-101`, `routes/task_routes.py:85-154` | Cálculo de relatórios, validações e criação de entidades direto nos handlers, apesar de existirem `models/` e `services/`. | AP-06 (`routes/task_routes.py:11-63`, …) e AP-03 (`routes/report_routes.py`) |
| 5 | HIGH | Modo debug e bind amplo ativos por padrão | `app.py:34` | `debug=True` com `host='0.0.0.0'` expõe o debugger interativo na rede. | AP-10 (`app.py:34`) |
| 6 | MEDIUM | N+1 queries | `routes/task_routes.py:41-51`, `routes/report_routes.py:55-56`, `routes/report_routes.py:161-163` | Para cada task busca usuário e categoria; para cada usuário/categoria uma nova contagem. | AP-11 (`routes/task_routes.py:41-57`, `routes/report_routes.py:53-68`) |
| 7 | MEDIUM | APIs deprecated | `models/task.py:15-16`, `routes/task_routes.py:31`, `routes/user_routes.py:29` | `datetime.utcnow()` é obsoleto desde Python 3.12 (usar `datetime.now(timezone.utc)`); `Query.get()` é API legada do SQLAlchemy 2.x (usar `db.session.get()`). | AP-15 (`models/task.py:15-16`, `routes/task_routes.py:42`, …) |
| 8 | MEDIUM | Código duplicado | `routes/task_routes.py:30-39`, `routes/task_routes.py:71-80`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-37` | Cálculo de "atrasada" repetido em 4 lugares enquanto `Task.is_overdue()` (`models/task.py:50-60`) não é usado. | AP-14 (`models/task.py:50-60`, `routes/task_routes.py:30-39`) |
| 9 | MEDIUM | Tratamento de erros genérico (`except:` nu) | `routes/task_routes.py:62`, `routes/task_routes.py:137`, `routes/report_routes.py:186` | Captura tudo (inclusive `KeyboardInterrupt`) e esconde a causa; sem handler centralizado. | AP-13 (`routes/task_routes.py:62`, …) |
| 10 | MEDIUM | Validação de entrada ausente | `routes/report_routes.py:196-202`, `routes/task_routes.py:113` | `PUT /categories/<id>` não verifica corpo nulo; prioridade não numérica causa `TypeError` (500). | AP-12 (`routes/task_routes.py:113-114`, `routes/report_routes.py:196-197`) |
| 11 | LOW | Imports não utilizados | `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:3-7` | `os`, `sys`, `json`, `time`, `math`, `hashlib` importados sem uso. | AP-20 (`app.py:7`, `routes/task_routes.py:7`) |
| 12 | LOW | `print` no lugar de logger | `routes/task_routes.py:149`, `routes/user_routes.py:83`, `utils/helpers.py:39` | Logs sem nível nem destino configurável. | AP-19 (`routes/task_routes.py:149`, `utils/helpers.py:39`) |
| 13 | LOW | Magic numbers ignorando constantes existentes | `routes/task_routes.py:96-114`, `routes/user_routes.py:64` | Limites `3`, `200`, `1..5` e `4` repetidos enquanto `utils/helpers.py:110-116` define as constantes. | AP-17 (`routes/task_routes.py:96`, `routes/user_routes.py:64`) |
| 14 | LOW | Nomes pobres | `routes/report_routes.py:24-28` | `p1`…`p5` escondem a semântica de prioridade. | AP-18 (`routes/report_routes.py:24-28`) |

## Construção da Skill

A skill está em `.claude/skills/refactor-arch/` dentro de cada projeto. A cópia canônica é a de
`code-smells-project/`; as outras duas são cópias idênticas (`diff -r` vazio).

```text
.claude/skills/refactor-arch/
├── SKILL.md                         # orquestração das 3 fases (230 linhas de corpo)
├── references/
│   ├── project-analysis.md          # área 1 — análise de projeto (Fase 1)
│   ├── anti-patterns-catalog.md     # área 2 — 20 anti-patterns (Fases 2 e 3)
│   ├── report-template.md           # área 3 — template do relatório (Fase 2)
│   ├── mvc-guidelines.md            # área 4 — regras do MVC alvo (Fase 3)
│   ├── refactoring-playbook.md      # área 5 — 18 transformações com antes/depois (Fase 3)
│   └── validation-protocol.md       # linha de base de comportamento, validação, evidência, reversão
└── scripts/                         # 8 scripts POSIX sh, testados nos 3 projetos
```

### Decisões de design

- **`SKILL.md` como prompt de orquestração, conhecimento nas referências (progressive
  disclosure).** O `SKILL.md` define regras não negociáveis, um checklist de progresso copiável,
  os passos e critérios de saída de cada fase e **quando** ler cada referência. Cada fase carrega
  só o que precisa: a Fase 1 lê a análise de projeto; a Fase 2, catálogo e template; a Fase 3,
  guidelines, playbook e protocolo de validação. Arquivos com mais de 100 linhas começam com
  sumário.
- **Um arquivo por área de conhecimento**, cada um identificável pelo título — a cobertura das 5
  áreas exigidas é verificável. O protocolo de validação ficou em arquivo próprio porque é longo
  e frágil (instruções de baixa liberdade).
- **Frontmatter:** `name: refactor-arch`; `description` em terceira pessoa, com o caso de uso
  primeiro e os termos-gatilho (auditoria arquitetural, anti-patterns, code smells, severidade,
  refatoração MVC, validação); `argument-hint: "[report-number]"` documenta o argumento opcional;
  `disable-model-invocation: true` porque a skill reescreve código e só deve rodar quando o
  usuário digita `/refactor-arch`. Não usamos `allowed-tools` (manteria o usuário fora do laço
  de permissões) nem `context: fork` (a Fase 2 precisa pausar e conversar no mesmo contexto).
- **Gate humano e segurança da Fase 3.** Fases 1–2 são somente leitura (a única escrita é o
  relatório em `reports/`). A pergunta `Proceed with refactoring (Phase 3)? [y/n]` encerra a
  resposta; sem ponto de restauração git limpo a skill imprime `Phase 3 is blocked: …` no lugar
  da pergunta. A Fase 3 captura a **linha de base de comportamento** da aplicação original (status
  e formato de cada endpoint), refatora, valida (boot + comparação + reauditoria com zero
  anti-patterns) e grava a evidência. Falha não é remendada: a skill diagnostica e oferece
  reverter o projeto ao `HEAD`.
- **Relatório e evidência gravados pela própria skill**, com `N` resolvido de forma genérica
  (argumento → relatório existente do mesmo projeto → próximo número livre).
- **Scripts para o que precisa ser determinístico**, cada um com cabeçalho de uso, saída
  `KEY=VALUE`, exit codes `0/1/2/3`, nenhum valor de projeto embutido e um procedimento manual
  equivalente descrito no `SKILL.md`:

  | Script | Para quê |
  |---|---|
  | `count-source-files.sh` | contar arquivos-fonte e linhas com exclusões padrão |
  | `check-restore-point.sh` | git presente e sem alterações pendentes fora de `.claude/` |
  | `resolve-output-path.sh` | caminho de `reports/audit-project-N.md` e `evidence/validation-project-N.md` |
  | `workspace-artifacts.sh` | detectar artefatos de runtime (bancos, caches) criados por uma execução |
  | `check-port.sh` | porta livre antes do boot (resposta de outro processo nunca conta) |
  | `wait-for-http.sh` | aguardar o boot exigindo que o processo iniciado continue vivo |
  | `probe-endpoints.sh` | executar o plano de requisições e gravar status, tipo e corpo |
  | `revert-project.sh` | reverter o projeto ao ponto de restauração preservando `.claude/` e ignorados |

### Anti-patterns do catálogo e por quê

O catálogo tem 20 entradas (`AP-01`–`AP-20`) com as quatro severidades do enunciado. Cada uma tem
sinais de detecção concretos com exemplos Python e Node, **falsos positivos** (essenciais para a
reauditoria com zero findings ser objetiva), impacto e os padrões do playbook que a eliminam.

| Severidade | Anti-patterns | Por quê |
|---|---|---|
| CRITICAL | AP-01 credenciais hardcoded · AP-02 SQL injection · AP-03 God class/file · AP-04 endpoint administrativo sem proteção · AP-05 senha em texto puro/hash fraco | exemplos literais da definição de CRITICAL do enunciado e problemas encontrados nos 3 projetos na Análise Manual (segredos nos 3, SQL concatenado e reset/SQL arbitrário no projeto 1, MD5 e base64 nos projetos 2 e 3) |
| HIGH | AP-06 regra de negócio em rotas · AP-07 estado global mutável · AP-08 acoplamento sem DI · AP-09 exposição de dados sensíveis · AP-10 debug/defaults inseguros | violações de MVC/SOLID citadas na definição de HIGH e vazamentos (senha na resposta, cartão no log, debugger exposto) |
| MEDIUM | AP-11 N+1 · AP-12 validação ausente · AP-13 tratamento de erros espalhado · AP-14 duplicação · AP-15 API deprecated · AP-16 callback hell | itens da definição de MEDIUM, a detecção de APIs deprecated exigida (com tabela obsoleto → moderno por stack) e o padrão assíncrono típico de Node legado |
| LOW | AP-17 magic numbers/strings · AP-18 nomes pobres · AP-19 print/console no lugar de logger · AP-20 imports/código morto | definição de LOW e o que precisa ser eliminado para a reauditoria chegar a zero |

O playbook tem 18 transformações (`TP-01`–`TP-18`), todas com antes/depois em Python/Flask e/ou
Node/Express, aplicadas na ordem segurança → estrutura → qualidade. Todo `AP` aponta para ao
menos um `TP`.

### Como a skill é agnóstica de tecnologia

- **Detecção por heurísticas**, não por nomes: manifestos (`requirements.txt`, `package.json`,
  `go.mod`, …), imports, padrões de bootstrap e declaração de rotas por framework, drivers de
  banco. Campo sem evidência vira `not detected`.
- **Exemplos multi-stack em domínio neutro** (biblioteca: `books`, `members`, `loans`) — nenhum
  nome de arquivo, rota, tabela ou domínio dos projetos-alvo nas regras. Verificado a cada
  mudança com uma busca pelos identificadores dos 3 projetos (zero ocorrências).
- **Estrutura MVC com default e critérios de adaptação:** mapeamento de diretórios para
  Python/Flask, Node/Express e notas para outras stacks; monolito → criar camadas; projeto com
  camadas parciais → preservar o que já cumpre as regras e mover só o necessário.
- **Scripts genéricos:** só `sh`, `git`, `curl`, `find`, `awk`, `sed`; todo valor de projeto
  (diretório, porta, URL, plano de requisições) entra por argumento; família de linguagem
  detectada por extensões com mapa extensível.
- **Mesma pasta nos 3 projetos**, byte a byte, provada por `diff -r`.

### Desafios e como foram resolvidos

O registro completo está em [`docs/iteration-log.md`](docs/iteration-log.md): 27 execuções reais da
skill (16 no projeto 1, 3 no projeto 2, 8 no projeto 3), 20 commits `fix(skill)` e o teste do fluxo
de falha. Cada falha seguiu o ciclo **reverter → corrigir a skill de forma genérica na cópia
canônica → sincronizar → reexecutar**, e cada execução foi auditada fora da skill (transcrição da
sessão, revisão independente do código e smoke test) antes de ser aceita. Os principais desafios:

| Desafio | Sintoma observado | Solução na skill |
|---|---|---|
| Relatório impresso ≠ gravado | o console omitiu os findings LOW que o arquivo tinha | a Fase 2 grava primeiro e imprime relendo o arquivo; posição fixa da linha `Deprecated APIs: none detected` |
| "Remendos" depois da validação | o agente corrigia o código após o primeiro boot e declarava CLEAN | validação de tentativa única + **fingerprint** do código no primeiro boot e no fim (`workspace-artifacts.sh fingerprint`) |
| Ordem das etapas | refatorou antes de capturar a linha de base de comportamento e usou `git stash` para voltar | gate de ordem com o marco `Behavior baseline captured`; proibição de comandos git que mudam estado |
| Autoauditoria complacente | reauditorias aprovavam N+1, validação sem tipo e literais remanescentes | revisão e reauditoria por **subagentes com contexto limpo**, rastreabilidade de cada finding original, matriz de validação e **varredura mecânica** com `grep` |
| Contradições entre catálogo e contrato | AP-12/AP-13 exigiam mudanças que quebrariam respostas do original | regras explícitas: só rejeições que evitam 5xx; capturas estreitas do driver para respostas de erro explícitas; diferenças pré-existentes são falso positivo |
| Laço de revisão sem convergência | 11 rodadas de revisores apontando minúcias de entradas malformadas | escopo do contrato restrito às respostas explícitas, achados só do catálogo, limite de 3 rodadas + rodada final nos arquivos alterados |
| Versão de API deprecated | `datetime.utcnow()` ignorado porque o projeto não declara versão do Python | versão de referência = declarada ou a do runtime registrada na Fase 1 |
| Idioma Active Record | revisores divergiam sobre `Model.query` em controllers | AP-06 aceita a API do model ORM em controllers e proíbe SQL bruto e consultas em rotas |
| Ambiente | porta 5000 (AirPlay no macOS), reloader do Flask sobrevivendo ao `pkill`, caches `__pycache__`, limites de uso da conta e reinício da máquina | `check-port.sh` com `LISTENER_PIDS`, parada por PID e filhos, `PYTHONDONTWRITEBYTECODE=1`, `revert-project.sh` remove diretórios vazios; falhas externas registradas e retomadas |

Como a skill mudou depois das primeiras execuções aceitas dos projetos 1 e 2, ambos foram
restaurados à linha de base do código e reexecutados com a versão final (commit `913dfc6` e
seguintes): os três resultados entregues correspondem à mesma versão da skill.

## Resultados

Todas as execuções entregues usam a mesma versão da skill (conteúdo idêntico nos 3 projetos;
commit `1ee20f3`, sincronizado em `b106f86`). Depois delas, a skill recebeu apenas uma correção de
texto do glossário ("linha de base" → "linha de base de comportamento", commits `d4bfd29`/`d04d774`),
sem mudança de comportamento; por decisão do autor, os projetos não foram reexecutados. Os resultados abaixo são os dos arquivos gravados
pela própria skill em [`reports/`](reports/) e [`evidence/`](evidence/).

### Findings por severidade

| Projeto | Stack detectada | Arquivos | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|---|---|
| code-smells-project | Python + Flask 3.1.1 | 4 | 5 | 4 | 4 | 4 | 17 | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | JavaScript (Node.js) + Express ^4.18.2 | 3 | 4 | 3 | 4 | 4 | 15 | [audit-project-2.md](reports/audit-project-2.md) |
| task-manager-api | Python + Flask 3.0.0 | 15 | 3 | 4 | 6 | 4 | 17 | [audit-project-3.md](reports/audit-project-3.md) |

Cobertura da Análise Manual (coluna *matched_by* acima): 14/14, 15/15 e 14/14 problemas
encontrados pela skill.

### Validação (evidências gravadas pela skill)

| Projeto | Resultado | Boot | Endpoints (linha de base de comportamento `captured`) | Reauditoria | Fingerprint | Evidência |
|---|---|---|---|---|---|---|
| code-smells-project | CLEAN | `python app.py` | 19/19 (16 ✓, 3 declared) | 0 anti-patterns | inalterado | [validation-project-1.md](evidence/validation-project-1.md) |
| ecommerce-api-legacy | CLEAN | `npm start` | 3/3 (2 ✓, 1 declared) | 0 anti-patterns | inalterado | [validation-project-2.md](evidence/validation-project-2.md) |
| task-manager-api | CLEAN | `python seed.py` + `python app.py` | 22/22 (18 ✓, 4 declared) | 0 anti-patterns | inalterado | [validation-project-3.md](evidence/validation-project-3.md) |

Cada evidência traz o trecho de log de boot da aplicação refatorada, a tabela endpoint a endpoint
(status e formato antes/depois) e as mudanças de contrato declaradas. Mudanças declaradas (todas
correções de segurança, exceto a observação do projeto 2 abaixo):

- **Projeto 1:** `senha` removida de `GET /usuarios` e `GET /usuarios/<id>`; `secret_key`, `debug`
  e `db_path` removidos de `GET /health`; `POST /admin/reset-db` e `POST /admin/query` exigem
  `X-Admin-Token` (403 sem `ADMIN_TOKEN` configurado, 401 com token inválido).
- **Projeto 2:** `GET /api/admin/financial-report` exige `X-Admin-Token`; o log do checkout não
  contém mais cartão nem chave do gateway; senha obrigatória para usuário novo no checkout (em vez
  da senha padrão `123456`); erro real de banco na busca do curso responde 500 em vez de 404.
- **Projeto 3:** o hash `password` saiu das respostas de `GET /users/<id>`, `POST /users`,
  `PUT /users/<id>` e `POST /login`.

### Estrutura antes e depois

Projeto 1 — code-smells-project (monolito → MVC):

```text
ANTES                         DEPOIS
app.py                        app.py                      # composition root (create_app)
controllers.py                config/settings.py          # ambiente; sem segredos literais
database.py                   database.py                 # conexão por requisição (flask.g), schema, seed
models.py                     models/                     # produto, usuario, pedido, admin, health
requirements.txt              controllers/                # regras: produto, usuario, pedido, relatorio, admin, health
                              views/                      # blueprints finos por domínio
                              middlewares/                # error_handler, auth (admin)
                              utils/                      # constants, errors, logger, security, validators
                              .env.example
```

Projeto 2 — ecommerce-api-legacy (God class → MVC em `src/`):

```text
ANTES                         DEPOIS
src/app.js                    src/app.js                  # composition root; start() com tratamento de erro
src/AppManager.js             src/config/index.js
src/utils.js                  src/database/connection.js  # sqlite3 promisificado
                              src/models/                 # user, course, enrollment, payment, auditLog, report
                              src/controllers/            # checkout, admin, user
                              src/routes/                 # express.Router finos
                              src/middlewares/            # errorHandler, asyncHandler, adminAuth
                              src/services/paymentGateway.js
                              src/utils/                  # constants, errors, logger, password, validators
                              .env.example
```

Projeto 3 — task-manager-api (camadas parciais → MVC completo):

```text
ANTES                         DEPOIS
app.py                        app.py                      # create_app; debug/host da config
database.py                   database.py
seed.py                       seed.py                     # mesmo comando; usa a fábrica e hash seguro
models/ (task, user,          models/ (task, user, category)   # preservados; métodos de domínio, utc_now
  category)                   controllers/ (task, user, report, category)   # nova camada de regras
routes/ (task, user, report)  routes/ (task, user, report)     # preservados, agora finos
services/notification_service.py   (removido: código morto com credenciais)
utils/helpers.py              utils/ (constants, errors, logger, metrics, security, time, validators)
                              config/settings.py, middlewares/error_handler.py, .env.example
```

### Checklist de validação

| Item | code-smells-project | ecommerce-api-legacy | task-manager-api |
|---|---|---|---|
| **Fase 1** — Linguagem detectada corretamente | ✅ Python | ✅ JavaScript (Node.js) | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express ^4.18.2 | ✅ Flask 3.0.0 |
| Domínio descrito corretamente | ✅ e-commerce | ✅ LMS com checkout | ✅ Task Manager |
| Número de arquivos condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 15 |
| **Fase 2** — Relatório segue o template | ✅ | ✅ | ✅ (com a observação sobre AP-15 abaixo) |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados por severidade | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 17 | ✅ 15 | ✅ 17 |
| Detecção de APIs deprecated (se aplicável) | ✅ none detected | ✅ none detected | ✅ `utcnow()`, `Query.get()` |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura de diretórios MVC | ✅ | ✅ | ✅ |
| Configuração extraída (sem hardcoded) | ✅ | ✅ | ✅ |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ `views/` | ✅ `src/routes/` | ✅ `routes/` |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ `app.py` | ✅ `src/app.js` | ✅ `app.py` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem corretamente | ✅ 19/19 | ✅ 3/3 | ✅ 22/22 |

### Observações por stack e nível de organização

- **Python/Flask vs. Node/Express:** a mesma skill gerou `create_app()` + Blueprints + conexão por
  requisição em Flask e um composition root com fábricas injetadas, driver promisificado,
  `async/await` e `asyncHandler` em Express. As regras de contrato foram decisivas no Node, onde o
  original responde erros em **texto puro**: o handler central reproduz esse formato.
- **Monolito vs. camadas parciais:** nos projetos 1 e 2 a skill criou todas as camadas; no
  projeto 3 preservou `models/` e `routes/`, criou `controllers/`, `config/` e `middlewares/`, e
  removeu código morto (`services/notification_service.py`, `utils/helpers.py`). O passo de seed
  continuou com o mesmo comando.
- **Projeto 2:** a resposta para erro real de banco na busca do curso passou de 404 para 500; o
  original tratava exceção e "não encontrado" no mesmo `if` por acidente — fora do escopo de
  contrato definido pela skill e declarado na evidência; não ocorre nas execuções.
- **Projeto 3:** o relatório registrou as duas APIs deprecated em dois blocos AP-15 (um por API,
  cada um com seu equivalente moderno) em vez de um bloco agrupado; contagens e `Total`
  continuam consistentes.
- **Ambiguidade documentada:** o banner de inicialização em `print` do projeto 1 foi tratado pela
  skill como saída de linha de comando (falso positivo do AP-19) em algumas execuções e como
  finding em outras; a versão final o substitui pelo logger.

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado
  (`claude --version`; `claude` abre a sessão e pede login se necessário).
- `git`, `curl`, `python3` (com o módulo `venv`) e `node` + `npm` no `PATH`.
- Portas livres: `5000` (projetos 1 e 3) e `3000` (projeto 2). No macOS, o **Receptor AirPlay**
  ocupa a porta 5000 — desative em Ajustes do Sistema → Geral → AirDrop e Handoff. Conferir com
  `lsof -nP -iTCP:5000 -sTCP:LISTEN` (sem saída = livre).
- Cada projeto sem alterações pendentes no git (é o ponto de restauração da Fase 3).

A skill instala as dependências do projeto sozinha, só no ambiente isolado do próprio projeto
(`.venv/` em Python, `node_modules/` em Node), ambos ignorados pelo git.

### Executar a skill

Inicie o Claude Code **dentro** do diretório do projeto (é assim que a skill de
`.claude/skills/refactor-arch/` é carregada) e invoque `/refactor-arch`. Ordem recomendada
1 → 2 → 3 (gera `reports/audit-project-1.md`, `-2.md`, `-3.md` sem argumentos):

```bash
cd code-smells-project && claude "/refactor-arch"
```

```bash
cd ecommerce-api-legacy && claude "/refactor-arch"
```

```bash
cd task-manager-api && claude "/refactor-arch"
```

Argumento opcional: o número do relatório (`claude "/refactor-arch 2"` grava
`reports/audit-project-2.md` e `evidence/validation-project-2.md`). Sem argumento, a skill
reutiliza o número de um relatório existente do mesmo projeto ou usa o próximo livre.

### O que esperar em cada fase

1. **Fase 1 — Análise:** banner `PHASE 1: PROJECT ANALYSIS` com linguagem, framework, banco,
   domínio, arquitetura, número de arquivos-fonte, tabelas, endpoints e estado do ponto de
   restauração, seguido do inventário de endpoints. Nada é alterado.
2. **Fase 2 — Auditoria:** relatório `ARCHITECTURE AUDIT REPORT` (findings ordenados de CRITICAL
   a LOW, com `arquivo:linha`), gravado automaticamente em `reports/audit-project-N.md`, e a
   pergunta `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`. Responder `n` encerra
   sem modificar nada. Com alterações pendentes no projeto, a skill imprime
   `Phase 3 is blocked: …` no lugar da pergunta.
3. **Fase 3 — Refatoração (após `y`):** a skill sobe a aplicação original e grava a linha de base
   de comportamento de todos os endpoints, reestrutura o projeto para MVC, sobe a versão
   refatorada, compara cada endpoint, reaudita o código (zero anti-patterns) e grava
   `evidence/validation-project-N.md`. Termina com `PHASE 3: REFACTORING COMPLETE` ou, em falha,
   `PHASE 3: REFACTORING FAILED` com diagnóstico e a oferta de reverter o projeto.

### Como validar a refatoração

- Leia `evidence/validation-project-N.md`: `Result: CLEAN`, trecho de boot, tabela de endpoints
  (linha de base de comportamento × depois, todos `✓` ou `declared`), mudanças de contrato declaradas e
  `Remaining anti-patterns: 0`.
- Suba a aplicação refatorada no ambiente isolado e chame endpoints. Os comandos abaixo são
  exemplos; a lista completa de endpoints exercitados pela skill, com status e formato esperados,
  está na tabela "Behavior baseline" de cada `evidence/validation-project-N.md`. Para parar o
  servidor, use `Ctrl+C` no terminal em que ele roda:

```bash
cd code-smells-project && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python app.py
```

```bash
curl -s http://127.0.0.1:5000/health
```

```bash
cd ecommerce-api-legacy && npm start
```

```bash
curl -s -X POST http://127.0.0.1:3000/api/checkout -H 'Content-Type: application/json' -d '{"usr":"Ana","eml":"ana@example.com","pwd":"senha","c_id":2,"card":"4111222233334444"}'
```

```bash
cd task-manager-api && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python seed.py && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python app.py
```

```bash
curl -s http://127.0.0.1:5000/tasks
```

  Endpoints administrativos protegidos pela refatoração exigem `ADMIN_TOKEN=<valor>` no ambiente
  ao subir a aplicação e o cabeçalho `X-Admin-Token: <valor>` na requisição (ver "Declared
  contract changes" de cada evidência). Depois de testar, apague os bancos locais gerados
  (`*.db`, `instance/`) — são ignorados pelo git.
- Compare a estrutura com a original: `git diff --stat 6d1ce62 -- <projeto>`.

### Reverter e reexecutar

- Em falha da Fase 3, responda `y` à pergunta `Revert project to the restore point? [y/n]`; a
  skill restaura o projeto ao `HEAD` preservando `.claude/`, `reports/`, `evidence/` e o ambiente
  isolado.
- Para reexecutar do zero um projeto já refatorado e commitado, restaure a linha de base do código
  (commit `6d1ce62`) fora de `.claude/`, commite e invoque a skill de novo (exemplo para o projeto 1):

```bash
git ls-files code-smells-project | grep -v '^code-smells-project/.claude/' | xargs git rm -q && git checkout 6d1ce62 -- code-smells-project && git commit -m "chore: restore code baseline of project 1"
```

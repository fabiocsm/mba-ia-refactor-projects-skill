# Análise de Projeto

Área de conhecimento 1. Heurísticas da Fase 1 para detectar linguagem, framework, banco de dados,
domínio e arquitetura atual, contar arquivos-fonte, inventariar endpoints e passos de execução.
A Fase 1 é **somente leitura**: não execute a aplicação, não instale nada e não crie arquivos.

## Sumário

- [1. Regra geral](#1-regra-geral)
- [2. Linguagem](#2-linguagem)
- [3. Framework e versão](#3-framework-e-versão)
- [4. Banco de dados](#4-banco-de-dados)
- [5. Domínio](#5-domínio)
- [6. Arquitetura atual](#6-arquitetura-atual)
- [7. Arquivos-fonte e linhas de código](#7-arquivos-fonte-e-linhas-de-código)
- [8. Inventário de endpoints](#8-inventário-de-endpoints)
- [9. Passos de execução](#9-passos-de-execução)
- [10. Ponto de restauração](#10-ponto-de-restauração)
- [11. Banner da Fase 1](#11-banner-da-fase-1)

## 1. Regra geral

- Toda conclusão precisa de evidência em arquivo (manifesto, import, declaração de rota).
- Campo que não pode ser identificado com evidência recebe `not detected` — nunca chute.
- Prefira o manifesto ao código para versões; prefira o código ao README para comportamento.

## 2. Linguagem

| Evidência | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, arquivos `.py` | Python |
| `package.json` + `.js/.mjs/.cjs` | JavaScript (Node.js) |
| `package.json` + `tsconfig.json` ou `.ts` | TypeScript (Node.js) |
| `go.mod` | Go |
| `pom.xml`, `build.gradle(.kts)` | Java/Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj` | C# |
| `Cargo.toml` | Rust |

- Em empate, vale a linguagem com mais arquivos-fonte (é o que `count-source-files.sh` usa).
- Versão da linguagem: a declarada (`python_requires`, `.python-version`, `engines.node`,
  `go 1.xx`). Se não houver, registre a versão do runtime disponível com um comando somente
  leitura (`.venv/bin/python --version` se o ambiente isolado existir, senão `python3 --version`;
  `node --version`) e informe `Python 3.x (runtime; não declarada)`. Essa é a versão de referência
  para APIs deprecated (AP-15).

## 3. Framework e versão

1. Procure o framework nas dependências declaradas e leia a versão como está no manifesto
   (`flask==3.1.1`, `"express": "^4.18.2"`). Para faixas (`^`, `~`, `>=`), informe a faixa.
2. Confirme no código de bootstrap:

   | Framework | Sinais no código |
   |---|---|
   | Flask | `Flask(__name__)`, `@app.route`, `Blueprint(`, `add_url_rule` |
   | FastAPI | `FastAPI()`, `@app.get`, `APIRouter` |
   | Django | `manage.py`, `urls.py`, `INSTALLED_APPS` |
   | Express | `require("express")`/`import express`, `express()`, `app.listen` |
   | Fastify/Koa/NestJS | `fastify()`, `new Koa()`, `@Controller()` |
   | Spring | `@RestController`, `@SpringBootApplication` |

3. `Dependencies:` lista as dependências de runtime declaradas além do framework, separadas por
   vírgula (sem dependências de desenvolvimento).

## 4. Banco de dados

| Sinal | Driver/ORM |
|---|---|
| `import sqlite3`, `sqlite3.connect(` | sqlite3 (stdlib) |
| `flask_sqlalchemy`, `sqlalchemy`, `SQLALCHEMY_DATABASE_URI` | SQLAlchemy |
| `require("sqlite3")`, `new sqlite3.Database(` | sqlite3 (Node) |
| `pg`, `mysql2`, `mongoose`, `prisma`, `sequelize`, `typeorm` | driver/ORM correspondente |

- Tipo: arquivo (`"app.db"`, `sqlite:///x.db`), memória (`":memory:"`, `sqlite://`), servidor
  (URL com host). Formato: `<driver/ORM> (<tipo>[: <arquivo>])`.
- `DB tables:` = nomes das tabelas/entidades encontradas em `CREATE TABLE`, `__tablename__`,
  classes de model ou schemas, na ordem em que aparecem.

## 5. Domínio

- Derive do vocabulário das entidades e das rotas (ex.: entidades `books`, `members`, `loans` e
  rotas `/loans/<id>/return` → "Biblioteca: acervo, membros e empréstimos").
- Formato: `<tipo de API> (<entidades principais>)`. Use o README do projeto só para confirmar.

## 6. Arquitetura atual

Classifique com base na distribuição real das responsabilidades:

| Classificação | Evidência |
|---|---|
| Monolítica — sem separação de camadas | rotas, regras e SQL nos mesmos poucos arquivos; uma classe/arquivo concentra tudo |
| Camadas parciais | existem pastas/módulos como `models/`, `routes/`, `services/`, `utils/`, mas rotas ainda acessam dados e contêm regras |
| MVC/camadas | rotas finas, controllers/services com regras, models com acesso a dados, config separada |

A classificação depende de **onde estão as responsabilidades**, não dos nomes dos arquivos: um
projeto com arquivos chamados `controllers`/`models` em que o módulo de dados também aplica regras
de negócio, as rotas ficam no entry point e não há config nem tratamento central de erros é
**Monolítica**. "Camadas parciais" exige pastas/pacotes por camada com ao menos uma camada
cumprindo seu papel.

Descreva em uma frase: `<classificação> — <evidência principal>` (ex.: "Monolítica — rotas, SQL e
regras em 3 arquivos sem separação de camadas").

## 7. Arquivos-fonte e linhas de código

- Execute `count-source-files.sh <projeto>`. `FILES` vai para `Source files:` e para o cabeçalho
  do relatório; `LOC` para `~<LOC> lines of code`.
- Definição: arquivo com extensão de código da linguagem predominante, excluindo `.claude/`,
  `.git/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `vendor/`, `dist/`, `build/`.
  Manifestos, lockfiles, documentação e exemplos de requisição (`.http`) não contam.
  `__init__.py` e scripts auxiliares da linguagem (seed, migração) contam.
- A lista de arquivos é a lista de auditoria da Fase 2: todos serão lidos.

## 8. Inventário de endpoints

Liste **todos** os endpoints. Para cada um registre `method`, `path`, `source` (`arquivo:linha`
da declaração), `params` (path/query/body esperados, lidos do handler) e `side_effect`:

| `side_effect` | Quando |
|---|---|
| `read` | só consulta |
| `create` | insere recurso |
| `update` | altera recurso existente |
| `delete` | remove recurso |
| `admin` | rota administrativa/diagnóstico ou ação global (reset, SQL arbitrário, relatórios privilegiados) |

Onde procurar:

| Stack | Declarações |
|---|---|
| Flask | `@app.route(path, methods=[...])`, `@<bp>.route(...)`, `app.add_url_rule(path, endpoint, view, methods=[...])`; prefixo de `register_blueprint(bp, url_prefix=...)` ou `Blueprint(..., url_prefix=...)`; sem `methods` = `GET` |
| Express | `app.<verbo>(path, ...)`, `router.<verbo>(path, ...)`, `app.use(prefix, router)`; `app.route(path).get(...).post(...)` |
| Outros | decorators/anotações de rota do framework (`@app.get`, `@GetMapping`) |

- Rotas com vários métodos geram uma entrada por método.
- Inclua rotas utilitárias (`/`, `/health`).
- Imprima o inventário logo após o banner da Fase 1, uma linha por endpoint:
  `<METHOD> <path> — <source> — <side_effect>`.

## 9. Passos de execução

Registre, sem executar:

- Instalação de dependências (manifesto e comando padrão da stack).
- Passos de setup documentados (README, `scripts` do `package.json`, script de seed/migração) e
  se são obrigatórios antes do boot.
- Comando de boot (README; `scripts.start` do `package.json`; `if __name__ == "__main__"` com
  `app.run`), porta e host (literal no código ou variável de ambiente) e uma URL de leitura para
  verificar o boot (prefira `/health` ou `/`).

## 10. Ponto de restauração

Execute `check-restore-point.sh <projeto>` e use `STATUS` em `Restore point:` — `ok`, `no-git` ou
`dirty (<PENDING> pending files)`. A Fase 1 apenas informa; a decisão de bloqueio é da Fase 2.

## 11. Banner da Fase 1

Formato exato (rótulos em inglês, conteúdo em português):

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem + versão se declarada>
Framework:     <framework + versão>
Dependencies:  <principais, separadas por vírgula>
Database:      <driver/ORM + tipo>
Domain:        <descrição curta>
Architecture:  <organização atual>
Source files:  <N> files analyzed
DB tables:     <entidades>
Endpoints:     <N> endpoints inventoried
Restore point: <ok | no-git | dirty (<k> pending files)>
================================
```

# Guidelines de Arquitetura MVC

Área de conhecimento 4. Regras do padrão MVC alvo da Fase 3: responsabilidades e proibições de
cada camada, mapeamento de diretórios por stack e critérios de adaptação ao nível de organização
encontrado.

## Sumário

- [1. Camadas, responsabilidades e proibições](#1-camadas-responsabilidades-e-proibições)
- [2. Fluxo de uma requisição](#2-fluxo-de-uma-requisição)
- [3. Mapeamento de diretórios por stack](#3-mapeamento-de-diretórios-por-stack)
- [4. Adaptação ao nível de organização](#4-adaptação-ao-nível-de-organização)
- [5. Preservação do contrato externo](#5-preservação-do-contrato-externo)
- [6. Execução, dependências e ambiente](#6-execução-dependências-e-ambiente)
- [7. Checklist de conformidade MVC](#7-checklist-de-conformidade-mvc)

## 1. Camadas, responsabilidades e proibições

| Camada | Responsabilidade | Proibido |
|---|---|---|
| **Config** | Ler configuração do ambiente (variáveis de ambiente) com defaults não sensíveis para boot local: porta, host, debug (`false`), caminho do banco, nível de log. Segredos só do ambiente, sem default literal. Expor um objeto/módulo de settings imutável. | Segredos literais; lógica de negócio; acesso a banco. |
| **Models** | Acesso a dados de uma entidade/agregado: consultas parametrizadas ou ORM, mapeamento linha → objeto/dicionário, transações de persistência. Um módulo por entidade. Schema e seed ficam junto da camada de dados (ex.: módulo `database`/`db`). | HTTP (`request`, `req`, `res`, `jsonify`); regras de negócio (descontos, aprovação, cálculos derivados que não são da própria entidade); criar a própria conexão fora do mecanismo da camada de dados. |
| **Views / Routes** | Declarar rotas; extrair parâmetros do request; chamar o validador; chamar o controller; serializar o resultado com o mesmo formato do original; mapear erros de domínio para status HTTP. | SQL/ORM; regra de negócio; `try/except` genérico; montar respostas de erro fora do padrão do projeto. |
| **Controllers** | Fluxo da aplicação e regras de negócio: orquestram models, aplicam validações de domínio, calculam valores, decidem transições, disparam notificações (via logger/serviço injetado). Retornam dados ou lançam erros de domínio. Em projetos que já têm `services/`, a regra pode morar em services chamados pelo controller — mantenha uma convenção única. | Objetos de request/response do framework; SQL direto; ler variáveis de ambiente. |
| **Middlewares** | Tratamento centralizado de erros (um único handler converte exceções em respostas), proteção de rotas administrativas, preocupações transversais (CORS, logging de requisição). | Regra de negócio. |
| **Entry point / composition root** | Criar a app, carregar config, inicializar banco/extensões, instanciar dependências e injetá-las, registrar rotas e middlewares, iniciar o servidor com host/porta/debug da config. | Regra de negócio; handlers de rota inline (exceto nenhum). |

Apoio permitido: `utils/` (logger, helpers puros sem estado), `validators/` (validação de
entrada na borda), `constants` (literais de domínio nomeados) — sempre sem estado mutável global.

## 2. Fluxo de uma requisição

```text
HTTP → route (views) → validator → controller → model → banco
                    ↖ serialização ← resultado ←┘
erro em qualquer ponto → error handler (middlewares) → resposta de erro no formato do projeto
```

- Erros de domínio são exceções/objetos de erro com status associado (ex.: `NotFoundError` →
  404, `ValidationError` → 400) definidos uma vez e tratados pelo handler central.
- O controller não conhece HTTP; a rota não conhece SQL.

## 3. Mapeamento de diretórios por stack

### Python / Flask (monolito → camadas)

```text
<projeto>/
├── app.py                    # entry point: create_app() (composition root) + execução
├── config/
│   ├── __init__.py
│   └── settings.py           # Settings a partir de os.environ
├── database.py               # conexão/extensão, schema e seed (ou models/db.py)
├── models/                   # <entidade>_model.py — acesso a dados
├── controllers/              # <dominio>_controller.py — regras e fluxo
├── views/ (ou routes/)       # <dominio>_routes.py — Blueprints finos
├── middlewares/
│   ├── error_handler.py      # register_error_handlers(app)
│   └── auth.py               # proteção de rotas administrativas (se houver)
└── utils/                    # logger, constantes, validadores
```

- Use **Blueprints** para agrupar rotas por domínio e registre-os no `create_app()`.
- Conexão `sqlite3`: abra por requisição via `flask.g` e feche em `teardown_appcontext`; o caminho
  vem da config; schema/seed rodam uma vez no `create_app()`.
- Flask-SQLAlchemy: mantenha `db = SQLAlchemy()` no módulo de dados e `db.init_app(app)` no
  `create_app()`.
- Mantenha um objeto `app` no módulo de entrada (`app = create_app()`) quando outros scripts ou
  comandos do projeto o importam (ex.: `from app import app`).

### Node.js / Express

```text
<projeto>/
└── src/
    ├── app.js                # entry point / composition root (mantém o comando de start)
    ├── config/index.js       # config a partir de process.env
    ├── database/             # conexão, schema, seed, helpers promisificados do driver
    ├── models/               # <entidade>Model.js — recebem a conexão por parâmetro/construtor
    ├── controllers/          # <dominio>Controller.js — regras e fluxo
    ├── routes/ (views)       # <dominio>Routes.js — express.Router finos
    ├── middlewares/          # errorHandler.js, asyncHandler.js, adminAuth.js
    └── utils/                # logger.js, constants.js, validators.js
```

- Express 4 não captura rejeições de handlers `async`: envolva-os com um `asyncHandler` que chama
  `next(err)`, e registre o middleware de erro (`(err, req, res, next)`) por último.
- Models e controllers são fábricas/classes que recebem dependências
  (`createBookModel(db)`, `new LoanController({ loanModel, logger })`) instanciadas no
  `app.js`.

### Outras stacks

Aplique o mesmo particionamento com a convenção da stack: Django (apps com `models.py`,
`views.py`, `services.py`, `urls.py`, settings por ambiente), FastAPI (`routers/`, `services/`,
`repositories/`, `core/config.py`, `Depends` para injeção), Spring (`controller/`, `service/`,
`repository/`, `config/`, `@ControllerAdvice`), Go (`handlers/`, `services/`, `repository/`,
`config/`, `main.go`). Mantenha a raiz de código existente (`src/`, `app/`, `cmd/`).

## 4. Adaptação ao nível de organização

| Situação | Ação |
|---|---|
| **Monolito** (tudo em poucos arquivos) | Criar as camadas da seção 3; dividir por domínio (TP-03); mover regras para controllers (TP-04); criar composition root (TP-05). |
| **Camadas parciais** (já há `models/`, `routes/`, `services/`…) | Preservar o que já cumpre as regras da seção 1 (ex.: models ORM corretos, blueprints); criar só as camadas que faltam (controllers, config, middlewares); mover regras e consultas para fora das rotas; corrigir violações pontuais. Não renomear pastas que já cumprem seu papel (`routes/` vale como views). |
| **Já em MVC** | Corrigir apenas os findings; não reestruturar. |

Critérios gerais:

- Mudanças estruturais só quando resolvem um finding ou uma proibição da seção 1.
- Preserve a raiz de código existente (`src/` em Node; raiz em Python) e o nome do módulo de
  entrada, para que o comando de boot continue o mesmo.
- Ao mover arquivos, atualize todos os imports e remova os arquivos antigos vazios (sem deixar
  módulos "ponte" sem uso, que seriam AP-20).
- Scripts auxiliares do projeto (seed, migração) continuam funcionando com o mesmo comando, usando
  a fábrica/composition root.

## 5. Preservação do contrato externo

Para cada endpoint inventariado na Fase 1, o código refatorado DEVE manter:

- método HTTP, path (incluindo conversores/tipos de parâmetros) e parâmetros aceitos;
- códigos de status para os mesmos cenários;
- tipo do corpo (JSON vs. texto) e o mesmo conjunto de chaves, nos mesmos níveis de aninhamento,
  com os mesmos nomes (inclusive nomes "ruins" impostos pelo contrato — renomeie só variáveis
  internas);
- mensagens e formato das respostas de erro já existentes (ex.: `{"error": "..."}` vs.
  `{"message": "..."}`; texto puro onde o original respondia texto).

Exceções permitidas, sempre **declaradas** no resumo da Fase 3 e na evidência:

- remoção de campo sensível da resposta (AP-09/TP-15);
- proteção/desabilitação de endpoint administrativo (AP-04/TP-14);
- qualquer outra mudança que seja a própria correção de um finding de segurança.

Entradas inválidas que antes geravam 500 podem passar a gerar 4xx (correção de AP-12/AP-13); elas
não entram na linha de base de comportamento (ver `validation-protocol.md`).

## 6. Execução, dependências e ambiente

- Os comandos de boot e setup documentados continuam válidos (ex.: `python app.py`,
  `npm start`, `python <seed>.py`). Se um comando precisar mudar, atualize o README do projeto e
  declare no resumo.
- Não adicione dependências de terceiros. Use a biblioteca padrão da linguagem ou o que já está
  instalado como dependência do framework (ex.: `werkzeug.security` em projetos Flask). Se uma
  dependência for indispensável, declare-a no manifesto e no resumo da Fase 3.
- Instalação somente no ambiente isolado dentro do projeto, cujo caminho é ignorado pelo git
  (Python: `.venv/`; Node: `node_modules/`). Nunca global.
- Configuração de exemplo vai em arquivo versionável (`.env.example`); nunca crie `.env`.
- Não altere `.claude/`, `reports/` nem arquivos fora do diretório do projeto.

## 7. Checklist de conformidade MVC

- [ ] Config extraída para módulo próprio; nenhum segredo literal; debug desligado por padrão.
- [ ] Models só com acesso a dados; um por entidade.
- [ ] Views/Routes só com roteamento, validação de borda e serialização.
- [ ] Controllers concentram regras e fluxo, sem objetos HTTP.
- [ ] Error handler centralizado registrado no composition root.
- [ ] Entry point claro que monta dependências e registra rotas.
- [ ] Todos os endpoints do inventário registrados com o mesmo método e path.
- [ ] Comandos de boot/setup inalterados (ou documentados).

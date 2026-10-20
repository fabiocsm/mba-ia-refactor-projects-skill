# Catálogo de Anti-patterns

Área de conhecimento 2. Usado na Fase 2 (auditoria) e na Fase 3 (reauditoria do código
refatorado). Cada anti-pattern tem identificador estável `AP-NN`, severidade, sinais de detecção
concretos, falsos positivos, impacto e os padrões de transformação (`TP-NN`) do
`refactoring-playbook.md` que o eliminam.

## Sumário

- [Escala de severidade](#escala-de-severidade)
- [Como auditar](#como-auditar)
- [Visão geral](#visão-geral)
- CRITICAL: [AP-01](#ap-01-hardcoded-credentialssecrets) · [AP-02](#ap-02-sql-injection-by-string-building) · [AP-03](#ap-03-god-classgod-file) · [AP-04](#ap-04-unprotected-administrativedebug-endpoint) · [AP-05](#ap-05-plaintext-or-weak-password-storage)
- HIGH: [AP-06](#ap-06-business-logic-in-route-handlers) · [AP-07](#ap-07-global-mutable-state) · [AP-08](#ap-08-tight-coupling-without-dependency-injection) · [AP-09](#ap-09-sensitive-data-exposure-in-responses-or-logs) · [AP-10](#ap-10-debug-mode-or-unsafe-defaults-enabled)
- MEDIUM: [AP-11](#ap-11-n1-queries--query-inside-loop) · [AP-12](#ap-12-missing-input-validation) · [AP-13](#ap-13-scattered-or-generic-error-handling) · [AP-14](#ap-14-duplicated-code) · [AP-15](#ap-15-deprecated-api-usage) · [AP-16](#ap-16-callback-hell)
- LOW: [AP-17](#ap-17-magic-numbersstrings) · [AP-18](#ap-18-poor-naming) · [AP-19](#ap-19-printconsole-logging-instead-of-logger) · [AP-20](#ap-20-unused-importsdead-code)

---

## Escala de severidade

Definições do enunciado, baseadas em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto,
  expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a
  separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e
  roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e
  testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem
  Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada
  (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas
  rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos
  pelo código.

A severidade de um finding é sempre a do anti-pattern no catálogo; não a ajuste caso a caso.

## Como auditar

1. Leia **todos** os arquivos-fonte listados na Fase 1, do início ao fim. Não audite por
   amostragem nem só pelos nomes dos arquivos.
2. Para cada arquivo, percorra os 20 anti-patterns na ordem do catálogo e compare com os sinais de
   detecção. Consulte os falsos positivos antes de registrar.
3. **Sem evidência, sem finding.** Só registre o que você consegue apontar em `arquivo:linha`.
   Nunca registre por suposição ("provavelmente existe").
4. **Uma ocorrência conta uma vez.** Agrupe todas as ocorrências do mesmo anti-pattern em um único
   finding e liste todas as localizações em `File:` (ex.: `a.py:10, a.py:42-48, b.py:7`). Se a
   mesma linha casar com dois anti-patterns, registre-a só no de maior severidade, exceto quando
   os problemas forem de natureza diferente (ex.: segredo hardcoded e o mesmo segredo devolvido
   na resposta: AP-01 e AP-09).
5. Verifique cada linha citada relendo o arquivo (ou com um comando pontual como
   `sed -n '<linha>p' <arquivo>`): a linha precisa mostrar o problema descrito.
6. API deprecated (AP-15) só é finding se a API constar da tabela do AP-15 ou tiver aviso de
   depreciação documentado pelo fornecedor para a versão declarada no manifesto.
7. Na **reauditoria** (Fase 3) aplique exatamente os mesmos sinais e falsos positivos ao código
   refatorado. Qualquer sinal remanescente, de qualquer severidade, é finding.

## Visão geral

| ID | Anti-pattern | Severidade | Categoria | Transformações |
|---|---|---|---|---|
| AP-01 | Hardcoded Credentials/Secrets | CRITICAL | segurança | TP-01 |
| AP-02 | SQL Injection by String Building | CRITICAL | segurança | TP-02 |
| AP-03 | God Class/God File | CRITICAL | arquitetura | TP-03, TP-04 |
| AP-04 | Unprotected Administrative/Debug Endpoint | CRITICAL | segurança | TP-14 |
| AP-05 | Plaintext or Weak Password Storage | CRITICAL | segurança | TP-09 |
| AP-06 | Business Logic in Route Handlers | HIGH | arquitetura | TP-04 |
| AP-07 | Global Mutable State | HIGH | SOLID | TP-05 |
| AP-08 | Tight Coupling without Dependency Injection | HIGH | SOLID | TP-05 |
| AP-09 | Sensitive Data Exposure in Responses or Logs | HIGH | segurança | TP-15, TP-11 |
| AP-10 | Debug Mode or Unsafe Defaults Enabled | HIGH | segurança | TP-01 |
| AP-11 | N+1 Queries / Query inside Loop | MEDIUM | performance | TP-07 |
| AP-12 | Missing Input Validation | MEDIUM | padronização | TP-08 |
| AP-13 | Scattered or Generic Error Handling | MEDIUM | padronização | TP-06 |
| AP-14 | Duplicated Code | MEDIUM | qualidade | TP-16 |
| AP-15 | Deprecated API Usage | MEDIUM | deprecated | TP-10 |
| AP-16 | Callback Hell | MEDIUM | qualidade | TP-13 |
| AP-17 | Magic Numbers/Strings | LOW | qualidade | TP-12 |
| AP-18 | Poor Naming | LOW | qualidade | TP-17 |
| AP-19 | Print/Console Logging instead of Logger | LOW | qualidade | TP-11 |
| AP-20 | Unused Imports/Dead Code | LOW | qualidade | TP-18 |

---

## CRITICAL

### AP-01 Hardcoded Credentials/Secrets

- **Severidade:** CRITICAL · **Categoria:** segurança · **Transformações:** TP-01
- **Sinais de detecção:**
  - Literal atribuído a nome que indica segredo — `secret`, `secret_key`, `password`, `passwd`,
    `pass`, `pwd`, `token`, `api_key`, `apikey`, `private_key`, `credential`, `dsn` com senha —
    em código ou em objeto de configuração versionado.
    Python: `app.config["SECRET_KEY"] = "abc123"`; Node: `const config = { dbPass: "s3cr3t" }`.
  - Chave de serviço externo com prefixo reconhecível (`sk_`, `pk_live_`, `AKIA`, `ghp_`) em
    literal.
  - Cliente de serviço externo (SMTP, banco, fila, API) construído com usuário/senha literais.
  - Variável de ambiente lida com **default secreto literal**:
    `os.environ.get("SECRET_KEY", "dev-secret")`, `process.env.API_KEY || "abc"`.
- **Falsos positivos:**
  - Leitura de ambiente sem default secreto: `os.environ.get("SECRET_KEY")`,
    `process.env.API_KEY ?? ""`, ou default gerado em tempo de execução
    (`secrets.token_hex(32)`, `crypto.randomBytes(32).toString("hex")`).
  - Valores não sensíveis com default literal (porta, host, caminho de banco local, nível de log).
  - Senhas de usuários de demonstração em seed/fixture (avaliadas por AP-05, não por AP-01).
  - Placeholders em arquivo de exemplo versionável (`.env.example`).
- **Impacto:** qualquer pessoa com acesso ao repositório obtém o segredo; troca exige deploy;
  segredos de produção vazam para forks e históricos.

### AP-02 SQL Injection by String Building

- **Severidade:** CRITICAL · **Categoria:** segurança · **Transformações:** TP-02
- **Sinais de detecção:**
  - Texto SQL montado com concatenação ou interpolação de **qualquer valor não constante**
    (inclusive ids convertidos com `str()`/`String()`) e passado a `execute`, `executemany`,
    `run`, `get`, `all`, `query`, `raw`, `text()`.
    Python: `"SELECT * FROM books WHERE id = " + str(book_id)`, `f"... LIKE '%{term}%'"`,
    `"... %s" % value`, `"...{}".format(v)`; Node: `` `SELECT * FROM books WHERE id = ${id}` ``,
    `"... WHERE title = '" + title + "'"`.
  - Cláusulas dinâmicas (`WHERE`, `ORDER BY`, `LIMIT`) montadas com valores do request.
  - Endpoints que executam SQL enviado pelo cliente são avaliados por AP-04, não por AP-02.
- **Falsos positivos:**
  - Placeholders do driver com parâmetros separados (`?`, `%s`, `:name`, `$1`):
    `cur.execute("... WHERE id = ?", (book_id,))`.
  - Query builders/ORM (`Model.query.filter(...)`, `select(Model).where(...)`), inclusive
    `column.like(f"%{term}%")` — o ORM parametriza o valor.
  - Concatenação apenas de fragmentos constantes (ex.: acrescentar `" AND active = 1"`) ou de
    placeholders, com os valores passados na lista de parâmetros.
- **Impacto:** leitura, alteração ou destruição arbitrária de dados; bypass de login.

### AP-03 God Class/God File

- **Severidade:** CRITICAL · **Categoria:** arquitetura · **Transformações:** TP-03, TP-04
- **Sinais de detecção:**
  - Um arquivo ou classe que contém, ao mesmo tempo, **(a)** roteamento/handlers HTTP ou
    bootstrap (criação de app, schema, seed), **(b)** regras de negócio e **(c)** acesso a dados
    (SQL/ORM). Ex.: classe que cria a conexão, define tabelas, popula dados, registra rotas e
    calcula valores.
  - Um módulo de dados que concentra acesso a dados **e** regras de negócio (cálculos, decisões,
    validação de estoque/saldo, descontos) de 3 ou mais entidades/domínios distintos.
  - Arquivo de rotas cujos handlers fazem consulta ORM/SQL **e** aplicam regra de negócio
    **e** serializam a resposta, para vários recursos.
- **Falsos positivos:**
  - Entry point/composition root que apenas monta dependências e registra rotas.
  - Arquivo pequeno de um único recurso já separado por camada (ex.: um model com consultas de
    uma entidade).
  - Model ORM com métodos de domínio simples da própria entidade (ex.: `is_overdue()`,
    `to_dict()`).
- **Impacto:** impossível testar em isolamento; qualquer mudança afeta tudo; conflitos de merge
  constantes; responsabilidades indistinguíveis.
- **Regra de desempate:** se o sinal de AP-03 estiver presente, não registre AP-06 para as
  mesmas linhas.

### AP-04 Unprotected Administrative/Debug Endpoint

- **Severidade:** CRITICAL · **Categoria:** segurança · **Transformações:** TP-14
- **Sinais de detecção:**
  - Rota com semântica administrativa ou de diagnóstico — prefixos `/admin`, `/debug`,
    `/internal`, `/ops`, ou nomes como `reset`, `seed`, `dump`, `query`, `exec` — **sem**
    verificação de autenticação/autorização antes da ação.
  - Endpoint que executa SQL, comandos ou expressões enviados pelo cliente.
  - Endpoint que apaga ou reinicializa todo o conjunto de dados, ou expõe dados agregados
    privilegiados (receita, relatórios gerenciais) sob rota administrativa sem proteção.
- **Falsos positivos:**
  - Endpoint administrativo protegido conforme TP-14: desabilitado por padrão (credencial lida do
    ambiente, sem default) e exigindo essa credencial quando habilitado.
  - CRUD comum de recursos em uma API que não possui modelo de autenticação: a ausência geral de
    autenticação é decisão de negócio fora do escopo deste catálogo.
  - Health check que só devolve status (sem segredos; ver AP-09).
- **Impacto:** qualquer cliente apaga a base, lê dados privilegiados ou executa SQL arbitrário.

### AP-05 Plaintext or Weak Password Storage

- **Severidade:** CRITICAL · **Categoria:** segurança · **Transformações:** TP-09
- **Sinais de detecção:**
  - Senha gravada como recebida ou comparada em texto puro (inclusive dentro do SQL:
    `WHERE email = ? AND password = ?`).
  - Hash rápido sem salt/stretching: `md5`, `sha1`, `sha256` simples
    (`hashlib.md5(pwd.encode()).hexdigest()`, `crypto.createHash("sha256")`).
  - Codificação reversível ou algoritmo caseiro (base64, XOR, truncamento) usado como "hash".
  - Senha padrão literal aplicada quando o cliente não envia uma (`pwd || "123456"`).
  - Seed/fixture que grava senhas de demonstração sem passar pela mesma função de hash.
- **Falsos positivos:**
  - KDF de senha com salt aleatório: `werkzeug.security.generate_password_hash`,
    `hashlib.scrypt`/`hashlib.pbkdf2_hmac` com salt de `secrets`, `crypto.scrypt`/`scryptSync`
    com salt de `crypto.randomBytes`, bcrypt/argon2 já declarados no manifesto.
  - Hash usado para fins que não são senha (checksum de arquivo, chave de cache).
- **Impacto:** vazamento do banco expõe todas as credenciais (e as reutilizadas em outros
  serviços).

---

## HIGH

### AP-06 Business Logic in Route Handlers

- **Severidade:** HIGH · **Categoria:** arquitetura · **Transformações:** TP-04
- **Sinais de detecção:**
  - Controller/service (camada de regras) que executa SQL ou ORM diretamente em vez de chamar um
    model (`db.execute(...)`, `cursor.execute(...)`, `Model.query...` dentro do controller).
  - Handler de rota (função decorada com `@app.route`/`@bp.route`, registrada com
    `add_url_rule`, callback de `app.get/post/...` ou `router.<verbo>`) que, além de ler o
    request e devolver a resposta: executa consultas SQL/ORM diretamente; calcula valores de
    negócio (totais, descontos, estatísticas, atraso); decide transições de estado; orquestra
    várias entidades; dispara notificações.
  - Handler com mais de um bloco de regras (ex.: valida estoque, calcula total, grava e notifica).
- **Falsos positivos:**
  - Handler que só faz: extrair parâmetros → chamar validador → chamar controller → serializar
    o resultado/mapear erro para status HTTP.
  - Validação de formato na borda delegada a um validador (ver TP-08).
- **Impacto:** regra de negócio presa ao framework HTTP; impossível reutilizar ou testar sem
  subir o servidor.

### AP-07 Global Mutable State

- **Severidade:** HIGH · **Categoria:** SOLID · **Transformações:** TP-05
- **Sinais de detecção:**
  - Variável de módulo reatribuída em tempo de execução (`global conn` em Python; `let` exportado
    ou de módulo reatribuído em Node).
  - Objeto/lista/dicionário de módulo mutado por funções de requisição (caches, contadores,
    acumuladores) — ex.: `cache[key] = value` em um `dict` global.
  - Conexão única de banco compartilhada entre requisições/threads criada sob demanda em variável
    global (ex.: `sqlite3.connect(..., check_same_thread=False)` guardada em global).
- **Falsos positivos:**
  - Constantes e configuração imutável carregada uma vez.
  - Objetos de framework criados uma vez e configurados no composition root: instância da app,
    extensões (`db = SQLAlchemy()` + `init_app`), blueprints/routers, logger.
  - Estado com dono explícito criado no composition root e injetado (ex.: instância de
    repositório ou cache passada aos controllers).
  - Conexão por requisição ligada ao contexto do framework (`flask.g` + `teardown_appcontext`).
- **Impacto:** condições de corrida, vazamento de estado entre requisições, testes
  interdependentes.

### AP-08 Tight Coupling without Dependency Injection

- **Severidade:** HIGH · **Categoria:** SOLID · **Transformações:** TP-05
- **Sinais de detecção:**
  - Classe/função de negócio ou de rotas que **instancia a própria infraestrutura** (conexão de
    banco, cliente SMTP/HTTP, driver) no construtor ou no corpo: `new sqlite3.Database(...)`,
    `smtplib.SMTP("smtp.host", 587)`, `new Client(...)`.
  - Componente que lê configuração diretamente de literais ou de um objeto global de config de
    outra camada, em vez de recebê-la.
  - Classe "gerenciadora" que cria e guarda tudo de que precisa, impossibilitando substituição
    em testes.
- **Falsos positivos:**
  - Dependências criadas no composition root e passadas por construtor/parâmetro/fábrica.
  - Acesso por mecanismo de contexto do framework configurado no composition root
    (`flask.g`/`current_app`, extensão inicializada com `init_app`, `req.app.locals`).
  - Import de módulos da camada imediatamente inferior (controller → model) quando esses módulos
    não criam infraestrutura própria.
- **Impacto:** impossível testar com dublês; trocar banco/serviço exige editar a regra de
  negócio.

### AP-09 Sensitive Data Exposure in Responses or Logs

- **Severidade:** HIGH · **Categoria:** segurança · **Transformações:** TP-15, TP-11
- **Sinais de detecção:**
  - Resposta HTTP que inclui senha/hash de senha, segredo, token de terceiros, chave de API,
    caminho interno de banco, flags de debug ou configuração (`to_dict()` com `password`;
    health check que devolve `secret_key`).
  - Serialização que devolve a linha inteira do banco (`SELECT *` → `dict(row)`) de entidade com
    campo sensível.
  - Log/print com dado sensível: número de cartão, senha, token, chave de API, segredo.
- **Falsos positivos:**
  - Campos sensíveis usados internamente e excluídos da serialização por allow-list.
  - Dados pessoais não secretos esperados pelo contrato (nome, e-mail do próprio recurso).
- **Impacto:** vazamento de credenciais e dados de pagamento para clientes e para quem lê logs.

### AP-10 Debug Mode or Unsafe Defaults Enabled

- **Severidade:** HIGH · **Categoria:** segurança · **Transformações:** TP-01
- **Sinais de detecção:**
  - Debug ligado por literal: `app.run(debug=True)`, `app.config["DEBUG"] = True`,
    `DEBUG = True`, `FLASK_DEBUG=1` hardcoded, `app.set("env", "development")` fixo.
  - Bind em todas as interfaces por padrão (`host="0.0.0.0"`) sem vir de configuração.
  - Ambiente declarado como produção enquanto debug está ativo.
- **Falsos positivos:**
  - Debug/host lidos da configuração com default seguro (`debug=False`, `127.0.0.1`).
  - Modo de desenvolvimento ativado apenas por variável de ambiente explícita.
- **Impacto:** debugger interativo exposto na rede permite execução remota de código; stack
  traces vazam detalhes internos.

---

## MEDIUM

### AP-11 N+1 Queries / Query inside Loop

- **Severidade:** MEDIUM · **Categoria:** performance · **Transformações:** TP-07
- **Sinais de detecção:**
  - Consulta de leitura executada uma vez por elemento de uma coleção — resultado de outra
    consulta ou itens do payload: `for loan in loans: cur.execute("SELECT ... WHERE id = ?", ...)`,
    `rows.forEach(r => db.get(...))`.
  - Acesso a relacionamento ORM carregado sob demanda dentro de laço (`book.author.name`,
    `len(member.loans)`) sem eager loading configurado na consulta.
  - `Model.query.get(id)`/`count()` por item dentro de laço.
  - Chamada a função de model/repositório que executa consulta, feita dentro de laço sobre uma
    coleção (a consulta está em outro arquivo, mas o N+1 é do laço que a chama).
- **Falsos positivos:**
  - Laço sobre coleção constante e pequena definida no código (ex.: lista fixa de status) — ainda
    assim prefira `GROUP BY`.
  - Escritas por item dentro de uma única transação quando não há API de lote no driver.
  - Consultas com `JOIN`, `IN (...)`, `GROUP BY` ou eager loading (`joinedload`, `selectinload`).
- **Impacto:** número de consultas cresce com o volume de dados; latência alta.

### AP-12 Missing Input Validation

- **Severidade:** MEDIUM · **Categoria:** padronização · **Transformações:** TP-08
- **Sinais de detecção:**
  - Elementos de listas recebidas no corpo (itens, linhas) usados sem validar cada elemento
    (tipo do elemento e de cada campo usado).
  - Corpo JSON usado sem verificar que existe e é objeto (`data.get(...)` com `data` possivelmente
    `None`; `req.body.x` sem checagem).
  - Valor do request usado em comparação numérica, aritmética ou persistência sem verificar tipo
    e faixa (`if priority < 1` com `priority` vindo do JSON).
  - Conversão de query/path param (`int()`, `float()`, `Number()`) sem tratar valor inválido.
  - Campo cujo uso pode gerar erro de execução — comparação, aritmética, `len()`, conversão,
    chamada de método, indexação — sem verificação de tipo antes (gera 500 com entrada inválida).
  - Regra de formato aplicada a um campo em um endpoint e ausente para o mesmo campo em outro
    (ex.: e-mail validado no cadastro e não na atualização).
- **Falsos positivos:**
  - Validação centralizada (validador/schema) chamada na borda antes do controller.
  - Tipos já garantidos pelo framework (`<int:id>` no Flask, conversores de rota).
  - Campo apenas repassado à persistência sem uso que possa falhar, ou ausência de regra de
    formato que o original também não tinha: passar a rejeitar entradas que o original aceitava
    mudaria o contrato (`mvc-guidelines.md` §5). Mantenha a regra de formato que já existia.
- **Impacto:** erros 500 com entradas inválidas, dados corrompidos, superfície de ataque maior.

### AP-13 Scattered or Generic Error Handling

- **Severidade:** MEDIUM · **Categoria:** padronização · **Transformações:** TP-06
- **Sinais de detecção:**
  - `except Exception`/`except:` em cada handler devolvendo 500, especialmente com `str(e)` no
    corpo da resposta.
  - `except:` nu (captura até `KeyboardInterrupt`/`SystemExit`) ou erro silenciado
    (`except: pass`).
  - Em Node, `err` de callback ignorado ou não verificado; promessa sem `catch`; rota assíncrona
    no Express 4 sem encaminhar a rejeição para `next(err)`.
  - Ausência de tratador central (`@app.errorhandler`, middleware de erro do Express).
- **Falsos positivos:**
  - Captura estreita de exceção esperada convertida em resposta de domínio (`ValueError` → 400,
    violação de unicidade → 409).
  - `try/except` que faz rollback e **relança** a exceção.
  - O próprio tratador central.
- **Impacto:** detalhes internos vazam para o cliente; erros ficam invisíveis; respostas de erro
  inconsistentes.

### AP-14 Duplicated Code

- **Severidade:** MEDIUM · **Categoria:** qualidade · **Transformações:** TP-16
- **Sinais de detecção:**
  - Mesmo bloco lógico (≥ 5 linhas equivalentes) em 2 ou mais lugares: validações, mapeamento
    linha→dicionário, cálculos derivados.
  - Mesma regra de negócio reimplementada em vários handlers (ex.: cálculo de "atrasado",
    totalização), especialmente quando já existe uma função/método equivalente.
  - Lista de valores válidos repetida em vários arquivos.
- **Falsos positivos:**
  - Estruturas paralelas pequenas (≤ 4 linhas) com significado diferente.
  - Código de teste e dados de seed.
- **Impacto:** correções precisam ser replicadas; as cópias divergem com o tempo.

### AP-15 Deprecated API Usage

- **Severidade:** MEDIUM · **Categoria:** deprecated · **Transformações:** TP-10
- **Sinais de detecção:** uso de API da tabela abaixo (ou com aviso de depreciação documentado
  pelo fornecedor para a versão declarada no manifesto). O finding DEVE indicar o equivalente
  moderno na `Recommendation`.

  | Stack | API obsoleta | Equivalente moderno |
  |---|---|---|
  | Python ≥ 3.12 | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
  | SQLAlchemy ≥ 2.0 / Flask-SQLAlchemy ≥ 3.0 | `Model.query.get(id)`, `session.query(M).get(id)` | `db.session.get(Model, id)` / `Session.get(Model, id)` |
  | Flask ≥ 2.3 | `@app.before_first_request` | inicialização no composition root/fábrica da app |
  | Python | `pkg_resources` | `importlib.metadata` / `importlib.resources` |
  | Node.js | `new Buffer(...)` | `Buffer.from(...)` / `Buffer.alloc(...)` |
  | Node.js | `url.parse(...)` | `new URL(...)` |
  | Node.js | `fs.exists(...)` | `fs.existsSync(...)` / `fs.promises.access(...)` |
  | Node.js | `crypto.createCipher(...)` | `crypto.createCipheriv(...)` |
  | Express 4 | `req.param(name)` | `req.params` / `req.query` / `req.body` |
  | Express 4 | `res.send(status, body)`, `res.json(status, obj)` | `res.status(status).send(body)` / `.json(obj)` |
  | Express 4 | `res.sendfile(...)`, `app.del(...)` | `res.sendFile(...)`, `app.delete(...)` |

- **Falsos positivos:** APIs apenas "antigas" sem depreciação documentada (callbacks do driver,
  `require`, `var`) — trate por outros anti-patterns se aplicável.
- **Impacto:** avisos em runtime, quebra em atualizações de versão, semântica incorreta (ex.:
  datetimes sem fuso).
- **Se nenhuma API deprecated for encontrada:** o relatório traz a linha
  `Deprecated APIs: none detected` antes do `Total`.

### AP-16 Callback Hell

- **Severidade:** MEDIUM · **Categoria:** qualidade · **Transformações:** TP-13
- **Sinais de detecção:**
  - Três ou mais níveis de callbacks assíncronos aninhados na mesma função
    (`db.get(..., () => { db.run(..., () => { db.run(..., () => {...}) }) })`).
  - Contadores manuais para sincronizar callbacks paralelos (`pending--; if (pending === 0)`).
  - Uso de `self`/`that` para contornar `this` em callbacks aninhados.
- **Falsos positivos:** um único callback de evento (`app.listen(port, () => ...)`); pipelines de
  promessas/`async`-`await` lineares.
- **Impacto:** fluxo ilegível, erros perdidos, respostas duplicadas ou nunca enviadas.

---

## LOW

### AP-17 Magic Numbers/Strings

- **Severidade:** LOW · **Categoria:** qualidade · **Transformações:** TP-12
- **Sinais de detecção:**
  - Literal numérico com significado de negócio em condição/cálculo fora de módulo de constantes
    ou config: limites, faixas, taxas, tamanhos mínimos/máximos (`if total > 10000`,
    `price * 0.1`, `len(title) < 3`).
  - Literal de domínio (status, papéis, tipos, prefixos de regra) repetido em 2+ lugares ou
    usado em condição fora do módulo de constantes (`status != "returned"`, `card.startsWith("4")`).
  - Listas de valores válidos declaradas inline em handlers.
- **Falsos positivos:**
  - `0`, `1`, `-1`, `""`, `None`/`null`, `True`/`False`.
  - Códigos de status HTTP (`200`, `201`, `400`, `404`...).
  - Literais dentro do módulo de constantes/config, definições de schema (tamanho de coluna,
    defaults de coluna), dados de seed/fixture, mensagens exibidas ao usuário, nomes de campos
    JSON e de colunas.
- **Impacto:** regra de negócio opaca; mudar um limite exige caçar todas as cópias.

### AP-18 Poor Naming

- **Severidade:** LOW · **Categoria:** qualidade · **Transformações:** TP-17
- **Sinais de detecção:**
  - Identificadores de uma letra ou abreviações crípticas que carregam dado de domínio fora de
    escopos mínimos (`u`, `e`, `p`, `cc`, `cid`, `d`, `x2`).
  - Nomes numerados para valores distintos (`p1`, `p2`, `cursor2`, `cursor3`).
  - Nomes que mentem sobre o conteúdo (`badCrypto`, `data2`, `tmp` para valor persistido).
- **Falsos positivos:**
  - Índices de laço curtos (`i`, `j`), variáveis de compreensão/lambda de uma linha, `e`/`err`
    para exceção, `req`/`res`/`next` no Express, `db`, `id`.
  - Nomes impostos por contrato externo: campos JSON do request/response, colunas do banco,
    nomes de rotas.
- **Impacto:** leitura lenta, erros de interpretação, revisão difícil.

### AP-19 Print/Console Logging instead of Logger

- **Severidade:** LOW · **Categoria:** qualidade · **Transformações:** TP-11
- **Sinais de detecção:**
  - `print(...)` (Python) ou `console.log/console.error/console.warn` (Node) em código da
    aplicação — handlers, controllers, models, services, middlewares, entry point — para
    registrar eventos, erros ou diagnóstico.
  - Notificações/efeitos simulados com print (`print("SENDING EMAIL ...")`).
- **Falsos positivos:**
  - A implementação do próprio módulo de logger (ex.: logger mínimo em Node que escreve em
    `process.stdout`).
  - Saída destinada ao usuário de scripts de linha de comando (ex.: mensagem final de um script
    de seed).
- **Impacto:** sem níveis, sem destino configurável, ruído em produção, dados sensíveis em
  stdout.

### AP-20 Unused Imports/Dead Code

- **Severidade:** LOW · **Categoria:** qualidade · **Transformações:** TP-18
- **Sinais de detecção:**
  - Import/require cujo nome nunca é usado no arquivo (`import os, sys, json` sem uso).
  - Função, classe, constante ou variável exportada/definida que nenhum outro ponto do projeto
    referencia (confirme com uma busca pelo nome em todos os arquivos-fonte).
  - Variável atribuída e nunca lida; parâmetro de configuração nunca usado; blocos comentados
    de código.
- **Falsos positivos:**
  - Re-exportações em `__init__.py`/`index.js` que definem a API pública do pacote.
  - Funções registradas por decorators/roteadores do framework (handlers, error handlers,
    comandos CLI) e entry points chamados por manifesto (`scripts` do `package.json`).
  - Imports feitos para efeito colateral necessário (registro de models/rotas).
- **Impacto:** ruído, falsa impressão de acoplamento, manutenção de código que não roda.

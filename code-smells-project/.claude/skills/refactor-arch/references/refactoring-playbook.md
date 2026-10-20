# Playbook de Refatoração

Área de conhecimento 5. Padrões concretos de transformação para cada anti-pattern do catálogo,
com exemplos **antes/depois** em Python/Flask e Node.js/Express. Os exemplos usam um domínio
neutro (biblioteca: `books`, `members`, `loans`) — adapte nomes, mensagens e formato de resposta
ao projeto refatorado, preservando o contrato externo (`mvc-guidelines.md` §5).

## Sumário

- [Ordem de aplicação](#ordem-de-aplicação)
- [Mapa AP → TP](#mapa-ap--tp)
- Segurança: [TP-01](#tp-01-extract-environment-backed-config) · [TP-02](#tp-02-parameterized-queries) · [TP-09](#tp-09-secure-password-hashing) · [TP-14](#tp-14-protect-or-disable-administrative-endpoints) · [TP-15](#tp-15-response-serialization-allow-list)
- Estrutura: [TP-03](#tp-03-split-god-class-by-domain-and-layer) · [TP-04](#tp-04-thin-routes--move-logic-to-controllers) · [TP-05](#tp-05-composition-root-and-dependency-injection) · [TP-06](#tp-06-centralized-error-handler)
- Qualidade: [TP-07](#tp-07-eliminate-n1-with-joineager-loadingbatch) · [TP-08](#tp-08-validate-input-at-the-boundary) · [TP-10](#tp-10-replace-deprecated-api) · [TP-11](#tp-11-structured-logger) · [TP-12](#tp-12-named-constants) · [TP-13](#tp-13-asyncawait-instead-of-nested-callbacks) · [TP-16](#tp-16-extract-shared-helper) · [TP-17](#tp-17-rename-for-intent) · [TP-18](#tp-18-remove-dead-code-and-unused-imports)

## Ordem de aplicação

1. **Segurança:** TP-01, TP-02, TP-09, TP-14, TP-15.
2. **Estrutura:** TP-03, TP-04, TP-05, TP-06.
3. **Qualidade:** TP-07, TP-08, TP-10, TP-11, TP-12, TP-13, TP-16, TP-17, TP-18.

Aplique os padrões de **todos** os findings do relatório. Ao terminar, o código não pode conter
nenhum sinal do catálogo (a reauditoria exige zero findings).

## Mapa AP → TP

| AP | TP | AP | TP |
|---|---|---|---|
| AP-01 | TP-01 | AP-11 | TP-07 |
| AP-02 | TP-02 | AP-12 | TP-08 |
| AP-03 | TP-03, TP-04 | AP-13 | TP-06 |
| AP-04 | TP-14 | AP-14 | TP-16 |
| AP-05 | TP-09 | AP-15 | TP-10 |
| AP-06 | TP-04 | AP-16 | TP-13 |
| AP-07 | TP-05 | AP-17 | TP-12 |
| AP-08 | TP-05 | AP-18 | TP-17 |
| AP-09 | TP-15, TP-11 | AP-19 | TP-11 |
| AP-10 | TP-01 | AP-20 | TP-18 |

---

## TP-01 Extract Environment-backed Config

- **Resolve:** AP-01, AP-10 · **Camada destino:** config · **Risco de contrato:** baixo
- **Passos:**
  1. Criar o módulo de config da seção 3 de `mvc-guidelines.md`.
  2. Segredos: ler do ambiente **sem default literal**; chave de assinatura ausente → gerar em
     runtime (`secrets.token_hex`/`crypto.randomBytes`); credencial de serviço ausente → vazia, e
     o recurso que depende dela fica desabilitado ou falha com erro claro ao ser usado.
  3. Não sensíveis (porta, host, caminho do banco, nível de log): default literal igual ao valor
     original, para o boot continuar idêntico. Debug: default `false`. Host: default `127.0.0.1`.
  4. Criar `.env.example` versionável com as chaves (valores vazios ou exemplos não secretos).
  5. Substituir todos os usos dos literais pela config.

Antes (Python):

```python
app = Flask(__name__)
app.config["SECRET_KEY"] = "library-secret-123"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
```

Depois (Python):

```python
# config/settings.py
import os
import secrets


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes")


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _env_bool("APP_DEBUG", False)
    HOST = os.environ.get("APP_HOST", "127.0.0.1")
    PORT = int(os.environ.get("APP_PORT", "8080"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "library.db")

# app.py
if __name__ == "__main__":
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
```

Antes (Node):

```js
const config = { dbPass: "s3cr3t", mailApiKey: "sk_live_abc", port: 4000 };
```

Depois (Node):

```js
// src/config/index.js
const config = Object.freeze({
  port: Number(process.env.PORT ?? 4000),
  host: process.env.HOST ?? "127.0.0.1",
  mailApiKey: process.env.MAIL_API_KEY ?? "",
  logLevel: process.env.LOG_LEVEL ?? "info",
});
module.exports = { config };
```

## TP-02 Parameterized Queries

- **Resolve:** AP-02 · **Camada destino:** model · **Risco de contrato:** baixo
- **Passos:** trocar toda interpolação por placeholders do driver; montar cláusulas dinâmicas
  concatenando apenas fragmentos constantes e acumulando os valores em uma lista de parâmetros;
  padrões `LIKE` vão como parâmetro (`f"%{term}%"`).

Antes (Python):

```python
cur.execute("SELECT * FROM books WHERE id = " + str(book_id))
query = "SELECT * FROM books WHERE 1=1"
if term:
    query += " AND title LIKE '%" + term + "%'"
cur.execute(query)
```

Depois (Python):

```python
cur.execute("SELECT * FROM books WHERE id = ?", (book_id,))
clauses, params = [], []
if term:
    clauses.append("title LIKE ?")
    params.append(f"%{term}%")
where = " AND ".join(clauses) or "1=1"
cur.execute(f"SELECT * FROM books WHERE {where}", params)
```

Antes (Node):

```js
db.all(`SELECT * FROM loans WHERE member_id = ${req.params.id}`, cb);
```

Depois (Node):

```js
const rows = await db.all("SELECT * FROM loans WHERE member_id = ?", [memberId]);
```

## TP-03 Split God Class by Domain and Layer

- **Resolve:** AP-03 · **Camada destino:** model, controller, view/route, entry point ·
  **Risco de contrato:** médio (rotas precisam ser registradas igualmente)
- **Passos:**
  1. Listar responsabilidades do arquivo/classe: bootstrap/schema/seed, rotas, regras, acesso a
     dados — e os domínios envolvidos.
  2. Criar um model por entidade (só acesso a dados), um controller por domínio (regras), um
     módulo de rotas por domínio (HTTP) e mover schema/seed para o módulo de dados.
  3. Mover funções sem alterar comportamento; depois aplicar TP-04/TP-05 nos pontos de contato.
  4. Remover o arquivo original quando vazio e atualizar todos os imports.

Antes (Node):

```js
class LibraryManager {
  constructor() { this.db = new sqlite3.Database(":memory:"); }
  initDb() { /* CREATE TABLE books ...; INSERT seed ... */ }
  setupRoutes(app) {
    app.post("/api/loans", (req, res) => { /* valida, consulta, calcula multa, grava */ });
  }
}
```

Depois (Node):

```js
// src/database/connection.js → createDatabase(), initSchema(db), seed(db)
// src/models/loanModel.js
function createLoanModel(db) {
  return {
    create: (memberId, bookId) => db.run("INSERT INTO loans (member_id, book_id) VALUES (?, ?)", [memberId, bookId]),
    findOpenByMember: (memberId) => db.all("SELECT * FROM loans WHERE member_id = ? AND returned_at IS NULL", [memberId]),
  };
}
// src/controllers/loanController.js → regras de empréstimo usando loanModel/bookModel
// src/routes/loanRoutes.js → router.post("/api/loans", asyncHandler(controller.create))
// src/app.js → composition root (TP-05)
```

Antes (Python): `storage.py` com consultas de `books`, `members` e `loans` + cálculo de multa +
baixa de exemplares.

Depois (Python):

```text
models/book_model.py      # SELECT/INSERT/UPDATE de books
models/member_model.py    # consultas de members
models/loan_model.py      # consultas de loans
controllers/loan_controller.py  # regra de multa, disponibilidade, orquestração
```

## TP-04 Thin Routes / Move Logic to Controllers

- **Resolve:** AP-03, AP-06 · **Camada destino:** controller, view/route ·
  **Risco de contrato:** médio
- **Passos:** a rota extrai parâmetros, chama o validador, chama o controller e serializa; o
  controller recebe valores simples, aplica as regras e chama os models; erros de domínio viram
  exceções tratadas pelo handler central (TP-06). Mantenha status e corpo idênticos.

Antes (Python):

```python
@bp.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json()
    book = Book.query.filter_by(id=data["book_id"]).first()
    if book.available_copies < 1:
        return jsonify({"error": "Sem exemplares"}), 400
    book.available_copies -= 1
    loan = Loan(member_id=data["member_id"], book_id=book.id)
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201
```

Depois (Python):

```python
# views/loan_routes.py
@bp.route("/loans", methods=["POST"])
def create_loan():
    payload = validate_loan_payload(request.get_json(silent=True))
    loan = loan_controller.create_loan(payload["member_id"], payload["book_id"])
    return jsonify(loan), 201

# controllers/loan_controller.py
def create_loan(member_id, book_id):
    book = book_model.get_by_id(book_id)
    if book is None:
        raise NotFoundError("Livro não encontrado")
    if book.available_copies < MIN_AVAILABLE_COPIES:
        raise ValidationError("Sem exemplares")
    return loan_model.create_and_reserve(member_id, book).to_dict()
```

Antes (Python, Flask-SQLAlchemy — consulta ORM no controller também é AP-06):

```python
# controllers/loan_controller.py
def overdue_loans():
    return Loan.query.filter(Loan.due_date < utc_now(), Loan.status == "open").all()
```

Depois (Python, Flask-SQLAlchemy):

```python
# models/loan.py
class Loan(db.Model):
    @classmethod
    def find_overdue(cls, now):
        return cls.query.filter(cls.due_date < now, cls.status == LOAN_STATUS_OPEN).all()

# controllers/loan_controller.py
def overdue_loans():
    return [loan.to_dict() for loan in Loan.find_overdue(utc_now())]
```

Antes (Node):

```js
app.get("/api/books/:id/stats", (req, res) => {
  db.all("SELECT * FROM loans WHERE book_id = ?", [req.params.id], (err, rows) => {
    const late = rows.filter((r) => r.due < Date.now() && !r.returned).length;
    res.json({ total: rows.length, late });
  });
});
```

Depois (Node):

```js
// routes/bookRoutes.js
router.get("/api/books/:id/stats", asyncHandler(async (req, res) => {
  res.json(await bookController.getStats(req.params.id));
}));
// controllers/bookController.js
async function getStats(bookId) {
  const loans = await loanModel.findByBook(bookId);
  return { total: loans.length, late: loans.filter(isLate).length };
}
```

## TP-05 Composition Root and Dependency Injection

- **Resolve:** AP-07, AP-08 · **Camada destino:** entry point · **Risco de contrato:** baixo
- **Passos:**
  1. Criar uma fábrica (`create_app(settings)` em Python; `buildApp(deps)`/bloco principal do
     `app.js` em Node) que carrega config, cria conexões/clientes, instancia models e
     controllers passando dependências, e registra rotas e middlewares.
  2. Eliminar variáveis globais mutáveis: conexão por requisição (`flask.g`) ou instância criada
     na fábrica e injetada; caches viram objetos com dono, injetados.
  3. Serviços externos (SMTP, gateways) recebem config no construtor.

Antes (Python):

```python
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("library.db", check_same_thread=False)
    return db_connection
```

Depois (Python):

```python
# database.py
import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_schema(get_db())

# app.py
def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    database.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(book_routes.bp)
    return app


app = create_app()
```

Antes (Node):

```js
let cache = {};
class Mailer { constructor() { this.client = new SmtpClient("smtp.example.com", "user", "pw"); } }
```

Depois (Node):

```js
// src/app.js (composition root)
const db = await createDatabase(config.databaseFile);
const mailer = createMailer({ host: config.smtpHost, user: config.smtpUser, password: config.smtpPassword });
const loanController = createLoanController({ loanModel: createLoanModel(db), mailer, logger });
app.use(createLoanRoutes(loanController));
```

## TP-06 Centralized Error Handler

- **Resolve:** AP-13 · **Camada destino:** middleware · **Risco de contrato:** médio (manter o
  formato de erro original)
- **Passos:**
  1. Definir erros de domínio uma vez (`AppError` com `status_code`; subclasses `NotFoundError`,
     `ValidationError`, `ConflictError`).
  2. Registrar um handler central que converte `AppError` no **mesmo formato de erro do projeto**
     (chave JSON usada, campos extras como flags de sucesso, ou texto puro) e qualquer outra
     exceção em 500 genérico sem detalhes internos, registrando-a no logger.
  3. Remover `try/except` genéricos dos handlers; manter apenas capturas estreitas (ex.:
     violação de unicidade → `ConflictError`) e rollback que relança.
  4. Não alterar as respostas padrão do framework para rotas inexistentes (404/405).
  5. Quando o contrato original tem uma resposta de erro **explícita** que depende de uma exceção
     (ex.: devolver a mensagem do erro do banco, ou `{"status": "error"}` no health check),
     reproduza-a capturando só o tipo de exceção do driver (`sqlite3.Error`, `SQLAlchemyError`)
     no controller ou convertendo-a em `AppError` com o mesmo corpo — nunca `except Exception`.

Antes (Python):

```python
def list_books():
    try:
        return jsonify({"data": book_model.all()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

Depois (Python):

```python
# utils/errors.py
class AppError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, extra=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.extra = extra or {}


class NotFoundError(AppError):
    status_code = 404

# middlewares/error_handler.py
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({ERROR_KEY: err.message, **err.extra}), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        logger.exception("Unhandled error")
        return jsonify({ERROR_KEY: GENERIC_ERROR_MESSAGE}), 500

# views/book_routes.py
def list_books():
    return jsonify({"data": book_controller.list_books()}), 200
```

Antes (Node):

```js
db.get(sql, [id], (err, row) => {
  if (err) return res.status(500).send("DB error");
  res.json(row);
});
```

Depois (Node):

```js
// src/utils/errors.js
class AppError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
// src/middlewares/asyncHandler.js
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
// src/middlewares/errorHandler.js — registrado por último no app.js
function createErrorHandler(logger) {
  return (err, req, res, next) => {
    if (err instanceof AppError) return res.status(err.status).send(err.message);
    logger.error("Unhandled error", { error: err.message });
    return res.status(500).send(GENERIC_ERROR_MESSAGE);
  };
}
```

Use `.send(text)` quando o projeto responde erros em texto e `.json({ <chave>: message })`
quando responde JSON — o formato é o do contrato original.

## TP-07 Eliminate N+1 with JOIN/Eager Loading/Batch

- **Resolve:** AP-11 · **Camada destino:** model · **Risco de contrato:** médio (mesmo formato,
  inclusive itens sem correspondência)
- **Passos:** substituir a consulta por item por uma consulta com `JOIN`/`LEFT JOIN`, `IN (...)`,
  `GROUP BY`, ou eager loading do ORM; montar a estrutura aninhada em memória preservando chaves,
  valores padrão (ex.: nome "desconhecido" quando o relacionamento não existe) e registros sem
  filhos (use `LEFT JOIN`).

Antes (Python, sqlite3):

```python
for loan in cur.execute("SELECT * FROM loans").fetchall():
    book = conn.execute("SELECT title FROM books WHERE id = ?", (loan["book_id"],)).fetchone()
    result.append({"id": loan["id"], "book_title": book["title"] if book else "Unknown"})
```

Depois (Python, sqlite3):

```python
rows = conn.execute(
    "SELECT l.id, b.title AS book_title FROM loans l LEFT JOIN books b ON b.id = l.book_id"
).fetchall()
result = [{"id": r["id"], "book_title": r["book_title"] or UNKNOWN_TITLE} for r in rows]
```

Antes (Python, SQLAlchemy):

```python
for loan in Loan.query.all():
    names.append(Member.query.get(loan.member_id).name)
```

Depois (Python, SQLAlchemy):

```python
from sqlalchemy.orm import joinedload

loans = Loan.query.options(joinedload(Loan.member)).all()
names = [loan.member.name for loan in loans]
# contagens por entidade: GROUP BY em vez de count() por item
counts = dict(db.session.query(Loan.member_id, func.count(Loan.id)).group_by(Loan.member_id).all())
```

Antes (Node):

```js
books.forEach((b) => db.all("SELECT * FROM loans WHERE book_id = ?", [b.id], (err, loans) => { /* ... */ }));
```

Depois (Node):

```js
const rows = await db.all(
  `SELECT b.id AS book_id, b.title, l.id AS loan_id, m.name AS member_name
     FROM books b
     LEFT JOIN loans l ON l.book_id = b.id
     LEFT JOIN members m ON m.id = l.member_id`
);
const byBook = new Map();
for (const row of rows) {
  if (!byBook.has(row.book_id)) byBook.set(row.book_id, { book: row.title, borrowers: [] });
  if (row.loan_id !== null) byBook.get(row.book_id).borrowers.push({ member: row.member_name ?? UNKNOWN_MEMBER });
}
const report = [...byBook.values()];
```

## TP-08 Validate Input at the Boundary

- **Resolve:** AP-12 · **Camada destino:** view/route (validators) · **Risco de contrato:** baixo
  para entradas válidas; mantenha status e mensagens das validações que já existiam
- **Passos:** criar validadores por recurso que verificam corpo presente e objeto, campos
  obrigatórios, tipos, faixas e formatos — **todo** campo do request usado em qualquer operação
  (comparação, aritmética, `len()`, conversão, indexação, função de biblioteca como hash de senha
  ou parse de data) tem o tipo verificado antes do uso (número:
  `int`/`float` excluindo `bool`; texto: `str`), inclusive campos de elementos de listas; regras
  de formato que o original já tinha são mantidas exatamente onde existiam, sem criar rejeições
  novas para entradas que o original aceitava; reproduzir na mesma ordem as validações e mensagens
  originais; lançar `ValidationError` (400) para o resto; chamar o validador na rota antes do
  controller.

Antes (Python):

```python
data = request.get_json()
if data["copies"] < 0:
    return jsonify({"error": "Quantidade inválida"}), 400
```

Depois (Python):

```python
# utils/validators.py
def validate_book_payload(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    copies = data.get("copies")
    if not isinstance(copies, int) or isinstance(copies, bool) or copies < MIN_COPIES:
        raise ValidationError("Quantidade inválida")
    return data
```

Antes (Node):

```js
if (!req.body.email) return res.status(400).send("Bad Request");
```

Depois (Node):

```js
// src/utils/validators.js
function validateLoanRequest(body) {
  const { memberEmail, bookId } = body ?? {};
  if (typeof memberEmail !== "string" || !EMAIL_PATTERN.test(memberEmail) || !Number.isInteger(Number(bookId))) {
    throw new AppError(BAD_REQUEST_MESSAGE, 400);
  }
  return { memberEmail, bookId: Number(bookId) };
}
```

## TP-09 Secure Password Hashing

- **Resolve:** AP-05 · **Camada destino:** model/controller (utils de segurança) ·
  **Risco de contrato:** baixo (login continua aceitando a mesma senha)
- **Passos:**
  1. Criar funções `hash_password`/`verify_password` com KDF e salt aleatório — Python:
     `werkzeug.security` (já presente em projetos Flask) ou `hashlib.scrypt`/`pbkdf2_hmac` +
     `secrets`; Node: `crypto.scryptSync` + `crypto.randomBytes` + `crypto.timingSafeEqual`.
  2. Gravar só o hash (cadastro, atualização, seed). Login: buscar por identificador e verificar
     o hash fora do SQL.
  3. Remover senhas padrão; senha ausente segue a regra de validação do endpoint.
  4. Em projetos cujo banco é recriado/semeado pelo próprio código, não manter verificação do
     formato antigo.

Antes (Python):

```python
member.password = hashlib.md5(raw.encode()).hexdigest()
row = cur.execute("SELECT * FROM members WHERE email = ? AND password = ?", (email, raw)).fetchone()
```

Depois (Python):

```python
from werkzeug.security import check_password_hash, generate_password_hash

member.password = generate_password_hash(raw)
row = cur.execute("SELECT * FROM members WHERE email = ?", (email,)).fetchone()
is_valid = row is not None and check_password_hash(row["password"], raw)
```

Antes (Node):

```js
const hash = Buffer.from(pwd || "123456").toString("base64");
```

Depois (Node):

```js
// src/utils/password.js
const crypto = require("node:crypto");

function hashPassword(password) {
  const salt = crypto.randomBytes(SALT_BYTES).toString("hex");
  const key = crypto.scryptSync(password, salt, KEY_LENGTH).toString("hex");
  return `${salt}:${key}`;
}

function verifyPassword(password, stored) {
  const [salt, key] = stored.split(":");
  const candidate = crypto.scryptSync(password, salt, KEY_LENGTH);
  return crypto.timingSafeEqual(candidate, Buffer.from(key, "hex"));
}
```

## TP-10 Replace Deprecated API

- **Resolve:** AP-15 · **Camada destino:** onde a API é usada · **Risco de contrato:** baixo
- **Passos:** substituir cada uso pela coluna "equivalente moderno" da tabela do AP-15,
  preservando a semântica:
  - Python `datetime.utcnow()` devolve datetime **sem fuso**. Se o valor é persistido ou
    comparado com colunas sem fuso (ex.: SQLite/SQLAlchemy `DateTime` padrão), use um helper
    que devolve UTC sem `tzinfo`, para não misturar naive/aware (`TypeError`) nem mudar o
    formato serializado.
  - Defaults de coluna recebem a função (sem chamar).

Antes (Python):

```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
if loan.due_date < datetime.utcnow():
    ...
member = Member.query.get(member_id)
```

Depois (Python):

```python
# utils/time.py
from datetime import datetime, timezone


def utc_now():
    """UTC atual sem tzinfo, compatível com colunas DateTime sem fuso."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

# models / controllers
created_at = db.Column(db.DateTime, default=utc_now)
if loan.due_date < utc_now():
    ...
member = db.session.get(Member, member_id)
```

Antes (Node):

```js
const parsed = url.parse(req.url);
const buf = new Buffer(text);
res.send(201, created);
```

Depois (Node):

```js
const parsed = new URL(req.url, `http://${req.headers.host}`);
const buf = Buffer.from(text);
res.status(201).send(created);
```

## TP-11 Structured Logger

- **Resolve:** AP-19, AP-09 (logs) · **Camada destino:** utils/entry point ·
  **Risco de contrato:** nenhum
- **Passos:** configurar o logger padrão da stack uma vez no composition root (nível pela
  config); substituir `print`/`console.*` por `logger.<nível>`; nunca registrar senhas, cartões,
  tokens ou segredos (registre identificadores ou valores mascarados); notificações simuladas
  viram `logger.info` com o evento.

Antes (Python):

```python
print("Loan created: " + str(loan_id) + " card " + card_number)
```

Depois (Python):

```python
# utils/logger.py
import logging


def configure_logging(level):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")

# controllers/loan_controller.py
logger = logging.getLogger(__name__)
logger.info("Loan created id=%s", loan_id)
```

Antes (Node):

```js
console.log(`Charging card ${card} with key ${config.apiKey}`);
```

Depois (Node):

```js
// src/utils/logger.js — sem dependências externas
const LEVELS = Object.freeze({ debug: 10, info: 20, warn: 30, error: 40 });

function createLogger(level = "info", stream = process.stdout) {
  const threshold = LEVELS[level] ?? LEVELS.info;
  const write = (name, message, meta = {}) => {
    if (LEVELS[name] < threshold) return;
    stream.write(`${JSON.stringify({ time: new Date().toISOString(), level: name, message, ...meta })}\n`);
  };
  return Object.freeze({
    debug: (m, meta) => write("debug", m, meta),
    info: (m, meta) => write("info", m, meta),
    warn: (m, meta) => write("warn", m, meta),
    error: (m, meta) => write("error", m, meta),
  });
}
// uso
logger.info("Payment processed", { loanId, cardLast4: card.slice(-4) });
```

## TP-12 Named Constants

- **Resolve:** AP-17 · **Camada destino:** constants/config · **Risco de contrato:** nenhum
- **Passos:** criar um módulo de constantes (por domínio ou global) com nomes que expliquem a
  regra; substituir todos os literais de negócio e listas de valores válidos; reutilizar
  constantes que já existem no projeto em vez de criar novas.

Antes (Python):

```python
if total_fees > 500:
    discount = total_fees * 0.1
if status not in ["open", "returned", "lost"]:
    ...
```

Depois (Python):

```python
# utils/constants.py
LOYALTY_DISCOUNT_THRESHOLD = 500
LOYALTY_DISCOUNT_RATE = 0.1
LOAN_STATUSES = ("open", "returned", "lost")

if total_fees > LOYALTY_DISCOUNT_THRESHOLD:
    discount = total_fees * LOYALTY_DISCOUNT_RATE
if status not in LOAN_STATUSES:
    ...
```

Antes (Node):

```js
const approved = card.startsWith("4");
```

Depois (Node):

```js
// src/utils/constants.js
const APPROVED_CARD_PREFIX = "4";
module.exports = { APPROVED_CARD_PREFIX };
// uso
const approved = card.startsWith(APPROVED_CARD_PREFIX);
```

## TP-13 Async/Await instead of Nested Callbacks

- **Resolve:** AP-16 · **Camada destino:** model/controller · **Risco de contrato:** médio
  (mesma resposta, mesma ordem de efeitos)
- **Passos:**
  1. Envolver o driver de callbacks em funções que retornam Promises (`run` devolve
     `lastID`/`changes`).
  2. Reescrever o fluxo como sequência `await`; paralelismo real com `Promise.all`.
  3. Rotas `async` passam pelo `asyncHandler` (TP-06).
  4. Inicialização do banco (schema/seed) é aguardada antes de `listen`, e a função de
     inicialização é chamada com tratamento de erro:
     `start().catch((err) => { logger.error("Startup failed", { error: err.message }); process.exitCode = 1; });`

Antes (Node):

```js
db.get("SELECT * FROM books WHERE id = ?", [bookId], (err, book) => {
  db.run("INSERT INTO loans (book_id, member_id) VALUES (?, ?)", [bookId, memberId], function (err) {
    const loanId = this.lastID;
    db.run("UPDATE books SET copies = copies - 1 WHERE id = ?", [bookId], (err) => {
      res.json({ loanId });
    });
  });
});
```

Depois (Node):

```js
// src/database/connection.js
function promisify(raw) {
  return {
    run: (sql, params = []) => new Promise((resolve, reject) => {
      raw.run(sql, params, function onRun(err) {
        if (err) reject(err); else resolve({ lastID: this.lastID, changes: this.changes });
      });
    }),
    get: (sql, params = []) => new Promise((resolve, reject) => raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)))),
    all: (sql, params = []) => new Promise((resolve, reject) => raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)))),
  };
}
// src/controllers/loanController.js
async function borrow(bookId, memberId) {
  const book = await bookModel.findById(bookId);
  if (!book) throw new AppError(BOOK_NOT_FOUND_MESSAGE, 404);
  const { lastID: loanId } = await loanModel.create(bookId, memberId);
  await bookModel.decrementCopies(bookId);
  return { loanId };
}
```

## TP-14 Protect or Disable Administrative Endpoints

- **Resolve:** AP-04 · **Camada destino:** middleware · **Risco de contrato:** alto — **mudança
  declarada** obrigatória
- **Passos:**
  1. Manter a rota (mesmo método e path) e mover a lógica para controller/model.
  2. Proteger com middleware/decorator: credencial administrativa lida do ambiente
     (`ADMIN_TOKEN`) **sem default**. Sem credencial configurada → endpoint desabilitado (403).
     Com credencial → exigir o cabeçalho `X-Admin-Token` com comparação em tempo constante;
     ausente/errado → 401.
  3. Documentar a variável em `.env.example` e declarar a mudança de contrato (rota, novo
     requisito, status quando desabilitada) no resumo da Fase 3 e na evidência.

Antes (Python):

```python
@app.route("/admin/rebuild-index", methods=["POST"])
def rebuild_index():
    get_db().execute("DELETE FROM search_index")
    return jsonify({"ok": True})
```

Depois (Python):

```python
# middlewares/auth.py
import hmac
from functools import wraps
from flask import current_app, request


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN")
        if not expected:
            raise AppError(ADMIN_DISABLED_MESSAGE, 403)
        provided = request.headers.get(ADMIN_TOKEN_HEADER, "")
        if not hmac.compare_digest(provided, expected):
            raise AppError(UNAUTHORIZED_MESSAGE, 401)
        return view(*args, **kwargs)
    return wrapper

# views/admin_routes.py
@bp.route("/admin/rebuild-index", methods=["POST"])
@require_admin
def rebuild_index():
    return jsonify(admin_controller.rebuild_index()), 200
```

Antes (Node):

```js
app.get("/api/admin/revenue", (req, res) => { /* consulta */ });
```

Depois (Node):

```js
// src/middlewares/adminAuth.js
const crypto = require("node:crypto");

function createAdminAuth(adminToken) {
  return (req, res, next) => {
    if (!adminToken) return next(new AppError(ADMIN_DISABLED_MESSAGE, 403));
    const provided = Buffer.from(req.get(ADMIN_TOKEN_HEADER) ?? "");
    const expected = Buffer.from(adminToken);
    if (provided.length !== expected.length || !crypto.timingSafeEqual(provided, expected)) {
      return next(new AppError(UNAUTHORIZED_MESSAGE, 401));
    }
    return next();
  };
}
// src/routes/adminRoutes.js
router.get("/api/admin/revenue", adminAuth, asyncHandler(async (req, res) => res.json(await adminController.revenue())));
```

## TP-15 Response Serialization Allow-list

- **Resolve:** AP-09 · **Camada destino:** model/view · **Risco de contrato:** alto quando remove
  campo — **mudança declarada**
- **Passos:** serializar entidades por lista explícita de campos públicos; remover da resposta
  senha/hash, segredos, caminhos internos e flags de debug; manter todos os demais campos com os
  mesmos nomes; declarar cada campo removido.

Antes (Python):

```python
def to_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email, "password": self.password}

@app.route("/health")
def health():
    return jsonify({"status": "ok", "secret_key": app.config["SECRET_KEY"], "db": DB_PATH})
```

Depois (Python):

```python
MEMBER_PUBLIC_FIELDS = ("id", "name", "email")

def to_dict(self):
    return {field: getattr(self, field) for field in MEMBER_PUBLIC_FIELDS}

@bp.route("/health")
def health():
    return jsonify(health_controller.status()), 200   # {"status": "ok", ...} sem segredos
```

Antes (Node):

```js
res.json(await db.get("SELECT * FROM members WHERE id = ?", [id]));
```

Depois (Node):

```js
const toPublicMember = ({ id, name, email }) => ({ id, name, email });
res.json(toPublicMember(await memberModel.findById(id)));
```

## TP-16 Extract Shared Helper

- **Resolve:** AP-14 · **Camada destino:** model/controller/utils · **Risco de contrato:** baixo
- **Passos:** escolher a implementação de referência (a que produz a resposta original), extrair
  para função/método único no nível certo (regra da entidade → model; regra de negócio →
  controller; transformação pura → utils), substituir todas as cópias e reutilizar helpers
  existentes no projeto em vez de criar novos.

Antes (Python):

```python
# em três handlers diferentes
if loan.due_date and loan.due_date < now and loan.status not in ("returned", "lost"):
    item["late"] = True
else:
    item["late"] = False
```

Depois (Python):

```python
# models/loan.py
def is_late(self, now):
    return bool(self.due_date) and self.due_date < now and self.status not in CLOSED_LOAN_STATUSES

# uso
item["late"] = loan.is_late(utc_now())
```

Antes (Node): o mesmo mapeamento `row → { id, title, author }` repetido em 4 funções.

Depois (Node):

```js
const toBook = (row) => ({ id: row.id, title: row.title, author: row.author });
const books = rows.map(toBook);
```

## TP-17 Rename for Intent

- **Resolve:** AP-18 · **Camada destino:** onde ocorre · **Risco de contrato:** nenhum (nunca
  renomeie campos do contrato externo nem colunas)
- **Passos:** renomear variáveis/funções internas para nomes de domínio; para campos de
  request/response com nomes ruins, renomeie apenas a variável interna que recebe o valor.

Antes (Node):

```js
const u = req.body.usr; const e = req.body.eml; const b = req.body.bk;
```

Depois (Node):

```js
const { usr: memberName, eml: memberEmail, bk: bookId } = req.body;
```

Antes (Python):

```python
p1 = Loan.query.filter_by(priority=1).count()
```

Depois (Python):

```python
urgent_loans = Loan.query.filter_by(priority=URGENT_PRIORITY).count()
```

## TP-18 Remove Dead Code and Unused Imports

- **Resolve:** AP-20 · **Camada destino:** onde ocorre · **Risco de contrato:** nenhum
- **Passos:** confirmar com busca no projeto que o nome não é usado (inclusive por decorators,
  registro dinâmico ou manifesto); remover imports, variáveis, funções, configuração e módulos
  sem uso; se um módulo inteiro sem uso contém um conceito útil, ligue-o ao fluxo pelo composition
  root **somente** se algum endpoint precisar dele — senão, remova.

Antes (Python):

```python
import os, sys, json
from utils.helpers import format_date, slugify

def list_books():
    return [b.to_dict() for b in Book.query.all()]
```

Depois (Python):

```python
def list_books():
    return [book.to_dict() for book in Book.query.all()]
```

Antes (Node):

```js
const { config, cache, totalFees } = require("./utils"); // cache e totalFees nunca usados
```

Depois (Node):

```js
const { config } = require("./config");
```

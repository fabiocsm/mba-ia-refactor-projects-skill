from database import get_db

CAMPOS_USUARIO = ("id", "nome", "email", "senha", "tipo", "criado_em")


def _to_dict(row):
    return {campo: row[campo] for campo in CAMPOS_USUARIO}


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_to_dict(row) for row in rows]


def get_por_id(usuario_id):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _to_dict(row) if row else None


def get_por_email(email):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    return _to_dict(row) if row else None


def criar(nome, email, senha_hash, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def contar():
    db = get_db()
    return db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

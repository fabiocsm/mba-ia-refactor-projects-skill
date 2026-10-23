from database import get_db
from utils.constants import TIPO_USUARIO_CLIENTE, USUARIO_PUBLIC_FIELDS


def _to_public_dict(row):
    return {field: row[field] for field in USUARIO_PUBLIC_FIELDS}


def listar():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_to_public_dict(row) for row in cursor.fetchall()]


def buscar_por_id(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _to_public_dict(row) if row else None


def buscar_por_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    return cursor.fetchone()


def criar(nome, email, senha_hash, tipo=TIPO_USUARIO_CLIENTE):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid

from database import get_db
from utils.constants import PRODUTO_FIELDS


def _to_dict(row):
    return {field: row[field] for field in PRODUTO_FIELDS}


def listar():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_to_dict(row) for row in cursor.fetchall()]


def buscar_por_id(produto_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return _to_dict(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def deletar(produto_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def buscar_por_ids(produto_ids):
    if not produto_ids:
        return {}
    db = get_db()
    cursor = db.cursor()
    placeholders = ",".join("?" * len(produto_ids))
    cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", produto_ids)
    return {row["id"]: _to_dict(row) for row in cursor.fetchall()}


def decrementar_estoque_em_lote(itens):
    db = get_db()
    cursor = db.cursor()
    cursor.executemany(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        [(quantidade, produto_id) for produto_id, quantidade in itens],
    )
    db.commit()


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    clauses = []
    params = []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        params.append("%" + termo + "%")
        params.append("%" + termo + "%")
    if categoria:
        clauses.append("categoria = ?")
        params.append(categoria)
    if preco_min:
        clauses.append("preco >= ?")
        params.append(preco_min)
    if preco_max:
        clauses.append("preco <= ?")
        params.append(preco_max)

    query = "SELECT * FROM produtos WHERE 1=1"
    if clauses:
        query += " AND " + " AND ".join(clauses)

    cursor.execute(query, params)
    return [_to_dict(row) for row in cursor.fetchall()]

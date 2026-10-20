from database import get_db

CAMPOS_PRODUTO = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")


def _to_dict(row):
    return {campo: row[campo] for campo in CAMPOS_PRODUTO}


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [_to_dict(row) for row in rows]


def get_por_id(produto_id):
    db = get_db()
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _to_dict(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def deletar(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    clauses = []
    params = []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        params.append(f"%{termo}%")
        params.append(f"%{termo}%")
    if categoria:
        clauses.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        params.append(preco_max)
    where = " AND ".join(clauses)
    query = "SELECT * FROM produtos" + (f" WHERE {where}" if where else "")
    rows = db.execute(query, params).fetchall()
    return [_to_dict(row) for row in rows]


def buscar_por_ids(produto_ids):
    if not produto_ids:
        return {}
    db = get_db()
    placeholders = ",".join("?" for _ in produto_ids)
    rows = db.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", produto_ids).fetchall()
    return {row["id"]: _to_dict(row) for row in rows}


def decrementar_estoque_em_lote(itens):
    db = get_db()
    db.executemany(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        [(item["quantidade"], item["produto_id"]) for item in itens],
    )
    db.commit()


def contar():
    db = get_db()
    return db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]

from database import get_db
from utils.constants import STATUS_PEDIDO_APROVADO, STATUS_PEDIDO_CANCELADO, STATUS_PEDIDO_PENDENTE


def get_todos():
    db = get_db()
    pedidos_rows = db.execute("SELECT * FROM pedidos").fetchall()
    return _montar_pedidos(db, pedidos_rows)


def get_por_usuario(usuario_id):
    db = get_db()
    pedidos_rows = db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    return _montar_pedidos(db, pedidos_rows)


def criar_registro(usuario_id, total, itens):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, STATUS_PEDIDO_PENDENTE, total),
    )
    pedido_id = cursor.lastrowid
    db.executemany(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        [(pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]) for item in itens],
    )
    db.commit()
    return pedido_id


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def obter_estatisticas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
    pendentes = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", (STATUS_PEDIDO_PENDENTE,)
    ).fetchone()[0]
    aprovados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", (STATUS_PEDIDO_APROVADO,)
    ).fetchone()[0]
    cancelados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", (STATUS_PEDIDO_CANCELADO,)
    ).fetchone()[0]
    return {
        "total_pedidos": total_pedidos,
        "faturamento": faturamento,
        "pendentes": pendentes,
        "aprovados": aprovados,
        "cancelados": cancelados,
    }


def contar():
    db = get_db()
    return db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def _montar_pedidos(db, pedidos_rows):
    pedido_ids = [row["id"] for row in pedidos_rows]
    itens_por_pedido = _buscar_itens_por_pedidos(db, pedido_ids)
    return [
        {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": itens_por_pedido.get(row["id"], []),
        }
        for row in pedidos_rows
    ]


def _buscar_itens_por_pedidos(db, pedido_ids):
    if not pedido_ids:
        return {}
    placeholders = ",".join("?" for _ in pedido_ids)
    rows = db.execute(
        f"""
        SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
        FROM itens_pedido ip
        LEFT JOIN produtos p ON p.id = ip.produto_id
        WHERE ip.pedido_id IN ({placeholders})
        """,
        pedido_ids,
    ).fetchall()
    agrupado = {}
    for row in rows:
        item = {
            "produto_id": row["produto_id"],
            "produto_nome": row["produto_nome"] if row["produto_nome"] is not None else "Desconhecido",
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"],
        }
        agrupado.setdefault(row["pedido_id"], []).append(item)
    return agrupado

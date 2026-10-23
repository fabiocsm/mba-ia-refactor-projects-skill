from database import get_db
from utils.constants import PEDIDO_PRODUTO_DESCONHECIDO


def _montar_pedidos(rows):
    pedidos = {}
    ordem = []
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pedido_id)
        if row["produto_id"] is not None:
            pedidos[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] else PEDIDO_PRODUTO_DESCONHECIDO,
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return [pedidos[pedido_id] for pedido_id in ordem]


_PEDIDOS_COM_ITENS_SQL = """
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario,
           pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    {where}
    ORDER BY p.id, i.id
"""


def criar(usuario_id, status, total, itens):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, status, total),
        )
        pedido_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            [(pedido_id, produto_id, quantidade, preco_unitario) for produto_id, quantidade, preco_unitario in itens],
        )
        cursor.executemany(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            [(quantidade, produto_id) for produto_id, quantidade, _ in itens],
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return pedido_id


def listar_por_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(_PEDIDOS_COM_ITENS_SQL.format(where="WHERE p.usuario_id = ?"), (usuario_id,))
    return _montar_pedidos(cursor.fetchall())


def listar_todos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(_PEDIDOS_COM_ITENS_SQL.format(where=""))
    return _montar_pedidos(cursor.fetchall())


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def contar_total():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    return cursor.fetchone()[0]


def somar_faturamento():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT SUM(total) FROM pedidos")
    total = cursor.fetchone()[0]
    return total if total is not None else 0


def contar_por_status(status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,))
    return cursor.fetchone()[0]

from database import get_db


def resetar():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()


def executar_sql(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    if query.strip().upper().startswith("SELECT"):
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    db.commit()
    return None

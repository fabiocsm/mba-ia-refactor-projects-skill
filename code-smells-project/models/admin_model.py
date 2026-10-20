from database import get_db
from utils.constants import SQL_SELECT_PREFIX, TIPO_QUERY_SELECT


def resetar():
    db = get_db()
    db.execute("DELETE FROM itens_pedido")
    db.execute("DELETE FROM pedidos")
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    db.commit()


def executar(query):
    db = get_db()
    cursor = db.execute(query)
    if query.strip().upper().startswith(SQL_SELECT_PREFIX):
        linhas = cursor.fetchall()
        return {"tipo": TIPO_QUERY_SELECT, "dados": [dict(row) for row in linhas]}
    db.commit()
    return {"tipo": "outro"}

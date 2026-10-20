import sqlite3

from models import pedido_model, produto_model, usuario_model
from utils.constants import APP_VERSION


def verificar_status():
    try:
        counts = {
            "produtos": produto_model.contar(),
            "usuarios": usuario_model.contar(),
            "pedidos": pedido_model.contar(),
        }
    except sqlite3.Error as e:
        return {"status": "erro", "detalhes": str(e)}, 500

    return (
        {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": APP_VERSION,
            "ambiente": "producao",
        },
        200,
    )

import sqlite3

from models import admin_model
from utils.logger import get_logger

logger = get_logger(__name__)


def resetar_banco():
    admin_model.resetar()
    logger.info("Banco de dados resetado")
    return {"mensagem": "Banco de dados resetado", "sucesso": True}


def executar_query(query):
    try:
        resultado = admin_model.executar_sql(query)
        if resultado is None:
            return {"mensagem": "Query executada", "sucesso": True}
        return {"dados": resultado, "sucesso": True}
    except sqlite3.Error as e:
        return {"erro": str(e)}, 500

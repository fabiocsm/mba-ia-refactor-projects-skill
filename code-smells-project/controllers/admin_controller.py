import sqlite3

from models import admin_model
from utils import logger
from utils.errors import AppError


def reset_database():
    admin_model.resetar()
    logger.info("Banco de dados resetado")


def executar_query(query):
    try:
        return admin_model.executar(query)
    except sqlite3.Error as e:
        raise AppError(str(e), status_code=500) from e

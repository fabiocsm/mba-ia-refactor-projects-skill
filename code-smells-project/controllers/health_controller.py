import sqlite3

from models import health_model


def status():
    try:
        counts = health_model.contagens()
        return {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": "1.0.0",
            "ambiente": "producao",
        }, 200
    except sqlite3.Error as e:
        return {"status": "erro", "detalhes": str(e)}, 500

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils import logger
from utils.constants import GENERIC_ERROR_MESSAGE
from utils.errors import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": err.message, **err.extra}), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        logger.error(f"Erro não tratado: {err}")
        return jsonify({"erro": GENERIC_ERROR_MESSAGE}), 500

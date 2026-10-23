from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError
from utils.logger import get_logger

logger = get_logger(__name__)

ERROR_KEY = "erro"
GENERIC_ERROR_MESSAGE = "Erro interno do servidor"


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        body = {ERROR_KEY: err.message}
        body.update(err.extra)
        return jsonify(body), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        logger.exception("Erro não tratado")
        return jsonify({ERROR_KEY: GENERIC_ERROR_MESSAGE}), 500

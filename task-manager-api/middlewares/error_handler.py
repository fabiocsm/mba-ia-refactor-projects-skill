import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.constants import ERROR_KEY, GENERIC_ERROR_MESSAGE
from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({ERROR_KEY: err.message, **err.extra}), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        if isinstance(err, HTTPException):
            return err
        logger.exception('Erro não tratado')
        return jsonify({ERROR_KEY: GENERIC_ERROR_MESSAGE}), 500

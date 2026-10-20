from flask import Blueprint, jsonify

from controllers import health_controller
from utils.constants import APP_VERSION

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": APP_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@bp.route("/health", methods=["GET"])
def health_check():
    body, status_code = health_controller.verificar_status()
    return jsonify(body), status_code

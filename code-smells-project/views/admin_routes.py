from flask import Blueprint, jsonify, request

from controllers import admin_controller
from middlewares.auth import require_admin
from utils.validators import validate_admin_query_payload

bp = Blueprint("admin", __name__)


@bp.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    resultado = admin_controller.resetar_banco()
    return jsonify(resultado), 200


@bp.route("/admin/query", methods=["POST"])
@require_admin
def executar_query():
    dados = request.get_json(silent=True)
    query = validate_admin_query_payload(dados)

    resultado = admin_controller.executar_query(query)
    if isinstance(resultado, tuple):
        body, status_code = resultado
        return jsonify(body), status_code
    return jsonify(resultado), 200

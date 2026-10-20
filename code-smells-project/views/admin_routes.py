from flask import Blueprint, jsonify, request

from controllers import admin_controller
from middlewares.auth import require_admin
from utils.constants import TIPO_QUERY_SELECT
from utils.validators import validate_admin_query

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/reset-db", methods=["POST"])
@require_admin
def reset_database():
    admin_controller.reset_database()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


@bp.route("/query", methods=["POST"])
@require_admin
def executar_query():
    query = validate_admin_query(request.get_json(silent=True))
    resultado = admin_controller.executar_query(query)
    if resultado["tipo"] == TIPO_QUERY_SELECT:
        return jsonify({"dados": resultado["dados"], "sucesso": True}), 200
    return jsonify({"mensagem": "Query executada", "sucesso": True}), 200

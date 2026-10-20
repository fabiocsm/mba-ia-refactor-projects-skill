from flask import Blueprint, jsonify

from controllers import relatorio_controller

bp = Blueprint("relatorios", __name__)


@bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    relatorio = relatorio_controller.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200

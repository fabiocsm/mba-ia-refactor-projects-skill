from flask import Blueprint, jsonify, request

from controllers import pedido_controller
from utils.validators import validate_pedido_payload, validate_status_pedido_payload

bp = Blueprint("pedidos", __name__)


@bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json(silent=True)
    usuario_id, itens = validate_pedido_payload(dados)
    resultado = pedido_controller.criar_pedido(usuario_id, itens)
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


@bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    return jsonify({"dados": pedido_controller.listar_todos_pedidos(), "sucesso": True}), 200


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_controller.listar_pedidos_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True)
    novo_status = validate_status_pedido_payload(dados)
    pedido_controller.atualizar_status_pedido(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

from flask import Blueprint, jsonify, request

from controllers import produto_controller
from utils.validators import validate_produto_busca, validate_produto_create

bp = Blueprint("produtos", __name__)


@bp.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = produto_controller.listar_produtos()
    return jsonify({"dados": produtos, "sucesso": True}), 200


@bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo, categoria, preco_min, preco_max = validate_produto_busca(request.args)
    resultados = produto_controller.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    produto = produto_controller.buscar_produto(produto_id)
    return jsonify({"dados": produto, "sucesso": True}), 200


@bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados_validados = validate_produto_create(request.get_json(silent=True))
    produto_id = produto_controller.criar_produto(dados_validados)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


@bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    produto_controller.atualizar_produto(produto_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    produto_controller.deletar_produto(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

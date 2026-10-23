from flask import Blueprint, jsonify, request

from controllers import usuario_controller
from utils.validators import validate_login_payload, validate_usuario_payload

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify({"dados": usuario_controller.listar_usuarios(), "sucesso": True}), 200


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    usuario = usuario_controller.buscar_usuario(usuario_id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json(silent=True)
    nome, email, senha = validate_usuario_payload(dados)
    resultado = usuario_controller.criar_usuario(nome, email, senha)
    return jsonify({"dados": resultado, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True)
    email, senha = validate_login_payload(dados)
    usuario = usuario_controller.login(email, senha)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200

from flask import Blueprint, jsonify, request

from controllers import usuario_controller
from utils.validators import validate_login, validate_usuario_create

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = usuario_controller.listar_usuarios()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    usuario = usuario_controller.buscar_usuario(usuario_id)
    return jsonify({"dados": usuario, "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    nome, email, senha = validate_usuario_create(request.get_json(silent=True))
    usuario_id = usuario_controller.criar_usuario(nome, email, senha)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    email, senha = validate_login(request.get_json(silent=True))
    usuario = usuario_controller.login(email, senha)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200

from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario_model
from utils.errors import AuthError, NotFoundError

CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")


def _serializar_publico(usuario):
    return {campo: usuario[campo] for campo in CAMPOS_PUBLICOS}


def listar_usuarios():
    usuarios = usuario_model.get_todos()
    return [_serializar_publico(usuario) for usuario in usuarios]


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_por_id(usuario_id)
    if usuario is None:
        raise NotFoundError("Usuário não encontrado")
    return _serializar_publico(usuario)


def criar_usuario(nome, email, senha):
    senha_hash = generate_password_hash(senha)
    return usuario_model.criar(nome, email, senha_hash)


def login(email, senha):
    usuario = usuario_model.get_por_email(email)
    if usuario is None or not check_password_hash(usuario["senha"], senha):
        raise AuthError("Email ou senha inválidos", extra={"sucesso": False})
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],
    }

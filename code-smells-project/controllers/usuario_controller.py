from models import usuario_model
from utils.constants import TIPO_USUARIO_CLIENTE
from utils.errors import NotFoundError, UnauthorizedError
from utils.security import hash_password, verify_password


def listar_usuarios():
    return usuario_model.listar()


def buscar_usuario(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def criar_usuario(nome, email, senha):
    senha_hash = hash_password(senha)
    usuario_id = usuario_model.criar(nome, email, senha_hash, TIPO_USUARIO_CLIENTE)
    return {"id": usuario_id}


def login(email, senha):
    row = usuario_model.buscar_por_email(email)
    if row and verify_password(senha, row["senha"]):
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
    raise UnauthorizedError("Email ou senha inválidos", extra={"sucesso": False})

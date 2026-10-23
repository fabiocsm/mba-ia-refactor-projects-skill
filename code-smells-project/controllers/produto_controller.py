from models import produto_model
from utils.errors import NotFoundError
from utils.validators import validate_produto_payload


def listar_produtos():
    return produto_model.listar()


def buscar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", extra={"sucesso": False})
    return produto


def criar_produto(payload):
    produto_id = produto_model.criar(**payload)
    return {"id": produto_id}


def atualizar_produto(produto_id, dados):
    produto_existente = produto_model.buscar_por_id(produto_id)
    if not produto_existente:
        raise NotFoundError("Produto não encontrado")

    payload = validate_produto_payload(dados, regras_criacao=False)
    produto_model.atualizar(produto_id, **payload)


def deletar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    produto_model.deletar(produto_id)


def buscar_produtos(termo, categoria, preco_min, preco_max):
    return produto_model.buscar(termo, categoria, preco_min, preco_max)

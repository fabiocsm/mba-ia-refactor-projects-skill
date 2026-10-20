from models import produto_model
from utils.errors import NotFoundError
from utils.validators import validate_produto_update


def listar_produtos():
    return produto_model.get_todos()


def buscar_produto(produto_id):
    produto = produto_model.get_por_id(produto_id)
    if produto is None:
        raise NotFoundError("Produto não encontrado", extra={"sucesso": False})
    return produto


def criar_produto(dados_validados):
    return produto_model.criar(**dados_validados)


def atualizar_produto(produto_id, dados_brutos):
    produto = produto_model.get_por_id(produto_id)
    if produto is None:
        raise NotFoundError("Produto não encontrado")
    dados_validados = validate_produto_update(dados_brutos)
    produto_model.atualizar(produto_id, **dados_validados)


def deletar_produto(produto_id):
    produto = produto_model.get_por_id(produto_id)
    if produto is None:
        raise NotFoundError("Produto não encontrado")
    produto_model.deletar(produto_id)


def buscar_produtos(termo, categoria, preco_min, preco_max):
    return produto_model.buscar(termo, categoria, preco_min, preco_max)

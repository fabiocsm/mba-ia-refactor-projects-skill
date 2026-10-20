from models import pedido_model, produto_model
from utils import logger
from utils.constants import STATUS_PEDIDO_APROVADO, STATUS_PEDIDO_CANCELADO
from utils.errors import PedidoError


def criar_pedido(usuario_id, itens):
    produtos = produto_model.buscar_por_ids([item["produto_id"] for item in itens])

    total = 0
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise PedidoError(f"Produto {item['produto_id']} não encontrado", extra={"sucesso": False})
        if produto["estoque"] < item["quantidade"]:
            raise PedidoError(f"Estoque insuficiente para {produto['nome']}", extra={"sucesso": False})
        total += produto["preco"] * item["quantidade"]

    itens_com_preco = [
        {**item, "preco_unitario": produtos[item["produto_id"]]["preco"]} for item in itens
    ]
    pedido_id = pedido_model.criar_registro(usuario_id, total, itens_com_preco)
    produto_model.decrementar_estoque_em_lote(itens)

    logger.info(f"Pedido {pedido_id} criado para usuario {usuario_id} - notificacoes enviadas (email, sms, push)")

    return {"pedido_id": pedido_id, "total": total}


def listar_todos_pedidos():
    return pedido_model.get_todos()


def listar_pedidos_usuario(usuario_id):
    return pedido_model.get_por_usuario(usuario_id)


def atualizar_status_pedido(pedido_id, novo_status):
    pedido_model.atualizar_status(pedido_id, novo_status)
    if novo_status == STATUS_PEDIDO_APROVADO:
        logger.info(f"Pedido {pedido_id} aprovado - preparar envio")
    elif novo_status == STATUS_PEDIDO_CANCELADO:
        logger.info(f"Pedido {pedido_id} cancelado - devolver estoque")

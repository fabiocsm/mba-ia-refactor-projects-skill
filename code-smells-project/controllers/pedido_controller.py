from models import pedido_model, produto_model
from utils.constants import STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE
from utils.errors import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)


def criar_pedido(usuario_id, itens):
    produtos = produto_model.buscar_por_ids([item["produto_id"] for item in itens])

    total = 0
    for item in itens:
        produto_id = item["produto_id"]
        quantidade = item["quantidade"]
        produto = produtos.get(produto_id)
        if produto is None:
            raise ValidationError(
                "Produto " + str(produto_id) + " não encontrado", extra={"sucesso": False}
            )
        if produto["estoque"] < quantidade:
            raise ValidationError(
                "Estoque insuficiente para " + produto["nome"], extra={"sucesso": False}
            )
        total = total + (produto["preco"] * quantidade)

    pedido_id = pedido_model.criar(usuario_id, STATUS_PENDENTE, total)

    pedido_model.adicionar_itens_em_lote(pedido_id, [
        (item["produto_id"], item["quantidade"], produtos[item["produto_id"]]["preco"])
        for item in itens
    ])
    produto_model.decrementar_estoque_em_lote([
        (item["produto_id"], item["quantidade"]) for item in itens
    ])

    logger.info("Pedido criado id=%s usuario_id=%s", pedido_id, usuario_id)
    logger.info("Notificacao enviada: email, sms e push para usuario_id=%s", usuario_id)

    return {"pedido_id": pedido_id, "total": total}


def listar_pedidos_usuario(usuario_id):
    return pedido_model.listar_por_usuario(usuario_id)


def listar_todos_pedidos():
    return pedido_model.listar_todos()


def atualizar_status_pedido(pedido_id, novo_status):
    pedido_model.atualizar_status(pedido_id, novo_status)

    if novo_status == STATUS_APROVADO:
        logger.info("Notificacao: pedido %s aprovado, preparar envio", pedido_id)
    if novo_status == STATUS_CANCELADO:
        logger.info("Notificacao: pedido %s cancelado, devolver estoque", pedido_id)

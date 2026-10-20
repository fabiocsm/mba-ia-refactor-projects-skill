from models import pedido_model
from utils import constants


def relatorio_vendas():
    stats = pedido_model.obter_estatisticas()
    faturamento = stats["faturamento"]

    if faturamento > constants.DESCONTO_FATURAMENTO_ALTO:
        desconto = faturamento * constants.DESCONTO_FATURAMENTO_ALTO_TAXA
    elif faturamento > constants.DESCONTO_FATURAMENTO_MEDIO:
        desconto = faturamento * constants.DESCONTO_FATURAMENTO_MEDIO_TAXA
    elif faturamento > constants.DESCONTO_FATURAMENTO_BAIXO:
        desconto = faturamento * constants.DESCONTO_FATURAMENTO_BAIXO_TAXA
    else:
        desconto = 0

    total_pedidos = stats["total_pedidos"]
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }

from models import pedido_model
from utils.constants import (
    DESCONTO_FAIXA_1_LIMITE,
    DESCONTO_FAIXA_1_TAXA,
    DESCONTO_FAIXA_2_LIMITE,
    DESCONTO_FAIXA_2_TAXA,
    DESCONTO_FAIXA_3_LIMITE,
    DESCONTO_FAIXA_3_TAXA,
    STATUS_APROVADO,
    STATUS_CANCELADO,
    STATUS_PENDENTE,
)


def relatorio_vendas():
    total_pedidos = pedido_model.contar_total()
    faturamento = pedido_model.somar_faturamento()
    pendentes = pedido_model.contar_por_status(STATUS_PENDENTE)
    aprovados = pedido_model.contar_por_status(STATUS_APROVADO)
    cancelados = pedido_model.contar_por_status(STATUS_CANCELADO)

    desconto = 0
    if faturamento > DESCONTO_FAIXA_1_LIMITE:
        desconto = faturamento * DESCONTO_FAIXA_1_TAXA
    elif faturamento > DESCONTO_FAIXA_2_LIMITE:
        desconto = faturamento * DESCONTO_FAIXA_2_TAXA
    elif faturamento > DESCONTO_FAIXA_3_LIMITE:
        desconto = faturamento * DESCONTO_FAIXA_3_TAXA

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }

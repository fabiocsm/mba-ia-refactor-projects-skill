from utils.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, STATUS_PEDIDO_VALIDOS
from utils.errors import ValidationError

NOME_PRODUTO_MIN_LEN = 2
NOME_PRODUTO_MAX_LEN = 200


def validate_produto_payload(dados, regras_criacao=True):
    if not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not isinstance(preco, (int, float)):
        raise ValidationError("Preço inválido")
    if not isinstance(estoque, (int, float)):
        raise ValidationError("Estoque inválido")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    if regras_criacao:
        if len(nome) < NOME_PRODUTO_MIN_LEN:
            raise ValidationError("Nome muito curto")
        if len(nome) > NOME_PRODUTO_MAX_LEN:
            raise ValidationError("Nome muito longo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def parse_preco_param(valor):
    if not valor:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValidationError("Parâmetro de preço inválido")


def validate_usuario_payload(dados):
    if not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not isinstance(senha, str):
        raise ValidationError("Nome, email e senha são obrigatórios")

    return nome, email, senha


def validate_login_payload(dados):
    if not isinstance(dados, dict):
        raise ValidationError("Email e senha são obrigatórios")

    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    if not isinstance(email, str) or not isinstance(senha, str):
        raise ValidationError("Email e senha são obrigatórios")

    return email, senha


def _coerce_produto_id(valor):
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        return int(valor) if valor.is_integer() else None
    if isinstance(valor, str):
        try:
            return int(valor)
        except ValueError:
            pass
        try:
            numero = float(valor)
        except ValueError:
            return None
        return int(numero) if numero.is_integer() else None
    return None


def validate_pedido_payload(dados):
    if not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not isinstance(itens, list) or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    itens_validados = []
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item do pedido inválido")
        produto_id = _coerce_produto_id(item.get("produto_id"))
        quantidade = item.get("quantidade")
        if produto_id is None:
            raise ValidationError("Item do pedido inválido")
        if not isinstance(quantidade, (int, float)):
            raise ValidationError("Item do pedido inválido")
        itens_validados.append({"produto_id": produto_id, "quantidade": quantidade})

    return usuario_id, itens_validados


def validate_admin_query_payload(dados):
    query = dados.get("sql", "") if isinstance(dados, dict) else ""

    if not isinstance(query, str) or not query:
        raise ValidationError("Query não informada")

    return query


def validate_status_pedido_payload(dados):
    novo_status = dados.get("status", "") if isinstance(dados, dict) else ""

    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")

    return novo_status

from utils.constants import (
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX_LEN,
    NOME_PRODUTO_MIN_LEN,
    STATUS_PEDIDO_VALIDOS,
)
from utils.errors import ValidationError


def _is_number(value):
    return isinstance(value, (int, float))


def _validar_campos_basicos_produto(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    if "nome" not in data:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in data:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in data:
        raise ValidationError("Estoque é obrigatório")

    nome = data["nome"]
    descricao = data.get("descricao", "")
    preco = data["preco"]
    estoque = data["estoque"]
    categoria = data.get("categoria", "geral")

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not _is_number(preco):
        raise ValidationError("Preço inválido")
    if not _is_number(estoque):
        raise ValidationError("Estoque inválido")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}


def validate_produto_create(data):
    campos = _validar_campos_basicos_produto(data)
    nome = campos["nome"]
    categoria = campos["categoria"]

    if len(nome) < NOME_PRODUTO_MIN_LEN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX_LEN:
        raise ValidationError("Nome muito longo")
    if not isinstance(categoria, str) or categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError(f"Categoria inválida. Válidas: {list(CATEGORIAS_VALIDAS)}")

    return campos


def validate_produto_update(data):
    campos = _validar_campos_basicos_produto(data)
    if not isinstance(campos["categoria"], str):
        raise ValidationError("Categoria inválida")

    return campos


def _parse_float_opcional(valor, nome_campo):
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"{nome_campo} inválido")


def validate_produto_busca(args):
    termo = args.get("q", "")
    categoria = args.get("categoria") or None
    preco_min = _parse_float_opcional(args.get("preco_min"), "preco_min")
    preco_max = _parse_float_opcional(args.get("preco_max"), "preco_max")
    return termo, categoria, preco_min, preco_max


def validate_usuario_create(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")

    nome = data.get("nome", "")
    email = data.get("email", "")
    senha = data.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not isinstance(nome, str) or not isinstance(email, str) or not isinstance(senha, str):
        raise ValidationError("Nome, email e senha são obrigatórios")

    return nome, email, senha


def validate_login(data):
    if not isinstance(data, dict):
        raise ValidationError("Email e senha são obrigatórios")

    email = data.get("email", "")
    senha = data.get("senha", "")

    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    if not isinstance(email, str) or not isinstance(senha, str):
        raise ValidationError("Email e senha são obrigatórios")

    return email, senha


def _normalizar_produto_id(produto_id):
    """Aceita int, float inteiro ou string numérica, como o SQL original aceitava via str()."""
    if isinstance(produto_id, int):
        return produto_id
    if isinstance(produto_id, float):
        return int(produto_id) if produto_id.is_integer() else produto_id
    if isinstance(produto_id, str):
        try:
            return int(produto_id)
        except ValueError:
            pass
        try:
            valor = float(produto_id)
        except ValueError:
            return None
        return int(valor) if valor.is_integer() else valor
    return None


def validate_pedido_create(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")

    usuario_id = data.get("usuario_id")
    itens = data.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not isinstance(itens, list) or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    itens_validados = []
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item do pedido inválido")
        produto_id = _normalizar_produto_id(item.get("produto_id"))
        quantidade = item.get("quantidade")
        if produto_id is None:
            raise ValidationError("produto_id do item é obrigatório e deve ser numérico")
        if not _is_number(quantidade):
            raise ValidationError("quantidade do item é obrigatória e deve ser numérica")
        itens_validados.append({"produto_id": produto_id, "quantidade": quantidade})

    return usuario_id, itens_validados


def validate_status_pedido(data):
    novo_status = data.get("status", "") if isinstance(data, dict) else ""
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return novo_status


def validate_admin_query(data):
    query = data.get("sql", "") if isinstance(data, dict) else ""
    if not isinstance(query, str) or not query:
        raise ValidationError("Query não informada")
    return query

CATEGORIA_PADRAO = "geral"
CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")

STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = (
    STATUS_PENDENTE,
    STATUS_APROVADO,
    STATUS_ENVIADO,
    STATUS_ENTREGUE,
    STATUS_CANCELADO,
)

TIPO_USUARIO_CLIENTE = "cliente"
TIPO_USUARIO_ADMIN = "admin"

DESCONTO_FAIXA_1_LIMITE = 10000
DESCONTO_FAIXA_1_TAXA = 0.1
DESCONTO_FAIXA_2_LIMITE = 5000
DESCONTO_FAIXA_2_TAXA = 0.05
DESCONTO_FAIXA_3_LIMITE = 1000
DESCONTO_FAIXA_3_TAXA = 0.02

ADMIN_TOKEN_HEADER = "X-Admin-Token"

PRODUTO_FIELDS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
USUARIO_PUBLIC_FIELDS = ("id", "nome", "email", "tipo", "criado_em")
PEDIDO_PRODUTO_DESCONHECIDO = "Desconhecido"

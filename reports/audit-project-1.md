================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Hardcoded Credentials/Secrets (AP-01)
File: app.py:7
Description: A chave de sessão do Flask é um literal fixo no código ("minha-chave-super-secreta-123") atribuído a app.config["SECRET_KEY"].
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões/cookies assinados; a troca da chave exige novo deploy e o valor já vazou no histórico do git.
Recommendation: Ler a chave de uma variável de ambiente sem default secreto, gerando um valor aleatório apenas em desenvolvimento (TP-01).

### [CRITICAL] SQL Injection by String Building (AP-02)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-161, models.py:163-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-280, models.py:289-299
Description: Praticamente todas as consultas de models.py são montadas por concatenação de string com valores vindos do request (ids convertidos com str(), nome/descricao/categoria, email/senha, termo de busca, preco_min/preco_max), em vez de usar placeholders parametrizados do driver sqlite3.
Impact: Permite leitura, alteração ou destruição arbitrária do banco e bypass de autenticação (ex.: login_usuario monta a cláusula WHERE com email e senha concatenados).
Recommendation: Substituir toda concatenação por placeholders "?" do sqlite3 com os valores passados na tupla de parâmetros de execute/executemany (TP-02).

### [CRITICAL] God Class/God File (AP-03)
File: models.py:105-120, models.py:133-169, models.py:235-273
Description: models.py concentra, no mesmo módulo, acesso a dados via SQL e regras de negócio de três domínios distintos (usuários/login, produtos/estoque e pedidos/faturamento): login_usuario decide autenticação, criar_pedido valida estoque e calcula o total do pedido, e relatorio_vendas aplica regras de desconto por faixa de faturamento — tudo misturado com os comandos SQL.
Impact: Impossível testar as regras de estoque, desconto ou autenticação sem banco de dados real; qualquer mudança de regra obriga a tocar no módulo de acesso a dados, e vice-versa.
Recommendation: Separar modelos (acesso a dados por entidade) de serviços de domínio (regras de estoque, totalização e desconto), conforme a estrutura em camadas (TP-03, TP-04).

### [CRITICAL] Unprotected Administrative/Debug Endpoint (AP-04)
File: app.py:47-57, app.py:59-78
Description: As rotas "/admin/reset-db" (apaga todas as tabelas) e "/admin/query" (executa qualquer SQL enviado no corpo da requisição) não exigem nenhuma autenticação ou credencial de administrador.
Impact: Qualquer cliente anônimo pode apagar toda a base de dados ou executar comandos SQL arbitrários, incluindo leitura, alteração ou exclusão de qualquer tabela.
Recommendation: Proteger as duas rotas com verificação de credencial de administrador lida do ambiente, desabilitadas por padrão quando a credencial não está configurada (TP-14).

### [CRITICAL] Plaintext or Weak Password Storage (AP-05)
File: database.py:75-83, models.py:105-120, models.py:122-131
Description: Senhas de usuários (inclusive as de seed: "admin123", "123456", "senha123") são gravadas e comparadas em texto puro, sem qualquer função de hash — criar_usuario insere a senha como recebida e login_usuario compara diretamente na cláusula SQL.
Impact: O vazamento do arquivo loja.db expõe todas as credenciais em texto puro, inclusive para reuso em outros serviços pelos mesmos usuários.
Recommendation: Gerar o hash da senha com uma KDF com salt (ex.: werkzeug.security.generate_password_hash) ao criar o usuário e usar generate_password_hash/check_password_hash no login, incluindo no seed (TP-09).

### [HIGH] Business Logic in Route Handlers (AP-06)
File: app.py:48-55, app.py:66-76, controllers.py:208-210, controllers.py:247-250, controllers.py:266-274
Description: Handlers de rota executam SQL diretamente (reset_database e executar_query em app.py; health_check em controllers.py faz suas próprias consultas) ou orquestram decisões de negócio e disparo de notificações (criar_pedido imprime envio de e-mail/SMS/push; atualizar_status_pedido decide notificar conforme o novo status), em vez de apenas chamar um model/serviço e serializar o resultado.
Impact: Regra de negócio e acesso a dados ficam presos ao framework HTTP, impedindo reuso e testes sem subir o servidor.
Recommendation: Mover o acesso a dados para models e a orquestração de notificações para um serviço de domínio chamado pelo controller (TP-04).

### [HIGH] Global Mutable State (AP-07)
File: database.py:4, database.py:7-10
Description: A conexão SQLite é mantida em uma variável global de módulo (db_connection), criada sob demanda com check_same_thread=False e reatribuída dentro de get_db(), sendo compartilhada por todas as requisições e threads.
Impact: Risco de condição de corrida entre requisições concorrentes e impossibilidade de isolar a conexão em testes.
Recommendation: Criar a conexão no composition root e injetá-la nos models, ou usar o contexto de aplicação do Flask (flask.g + teardown_appcontext) para uma conexão por requisição (TP-05).

### [HIGH] Sensitive Data Exposure in Responses or Logs (AP-09)
File: models.py:72-87, models.py:89-103, controllers.py:128-134, controllers.py:136-144, controllers.py:285-289
Description: As consultas de usuário devolvem a linha completa do banco, incluindo o campo "senha", e os controllers listar_usuarios/buscar_usuario repassam esse dado na resposta HTTP; health_check devolve ainda "secret_key" e "debug": True diretamente no JSON de resposta.
Impact: Qualquer cliente da API obtém a senha de qualquer usuário e a chave de sessão da aplicação só por consultar endpoints de leitura.
Recommendation: Serializar usuários por allow-list sem o campo de senha e remover secret_key/debug do corpo de health_check (TP-15, TP-11).

### [HIGH] Debug Mode or Unsafe Defaults Enabled (AP-10)
File: app.py:8, app.py:88
Description: app.config["DEBUG"] é fixado em True e app.run() é chamado com debug=True e host="0.0.0.0", ligando a aplicação a todas as interfaces de rede com o debugger interativo ativo por padrão.
Impact: O debugger interativo do Werkzeug exposto na rede permite execução remota de código a partir de qualquer cliente que alcance a porta.
Recommendation: Ler debug/host de configuração com default seguro (debug=False, host 127.0.0.1) e ativar modo de desenvolvimento só por variável de ambiente explícita (TP-01).

### [MEDIUM] N+1 Queries / Query inside Loop (AP-11)
File: models.py:139-146, models.py:154-166, models.py:187-199, models.py:219-231
Description: criar_pedido consulta o produto uma vez por item do pedido (duas vezes: para validar estoque e para gravar o preço unitário) dentro de laços; get_pedidos_usuario e get_todos_pedidos consultam itens_pedido por pedido e, para cada item, consultam o nome do produto, tudo dentro de laços aninhados.
Impact: O número de consultas ao banco cresce linearmente com a quantidade de itens/pedidos, degradando a latência conforme o volume de dados aumenta.
Recommendation: Substituir as consultas em laço por JOIN ou por uma consulta com IN (...) que traga todos os produtos/itens de uma vez (TP-07).

### [MEDIUM] Missing Input Validation (AP-12)
File: controllers.py:43-46, controllers.py:87-90, controllers.py:118-121, controllers.py:195-201, app.py:61-62
Description: preco/estoque são comparados numericamente sem verificar que são números (criar_produto e atualizar_produto); preco_min/preco_max são convertidos com float() sem tratar valor inválido (buscar_produtos); os itens do corpo de criar_pedido são usados (item["produto_id"], item["quantidade"]) sem validar a presença/tipo de cada campo; em /admin/query, dados.get("sql", "") é chamado sem verificar que request.get_json() retornou um objeto.
Impact: Entradas malformadas geram erro 500 em vez de uma resposta 400 clara, e abrem superfície para exceções não tratadas.
Recommendation: Validar tipo e presença de cada campo do corpo/query antes de usá-lo em comparação, conversão ou acesso por chave (TP-08).

### [MEDIUM] Scattered or Generic Error Handling (AP-13)
File: controllers.py:10, controllers.py:21, controllers.py:60, controllers.py:95, controllers.py:108, controllers.py:125, controllers.py:133, controllers.py:143, controllers.py:164, controllers.py:185, controllers.py:218, controllers.py:226, controllers.py:234, controllers.py:254, controllers.py:261, controllers.py:291, app.py:77
Description: Todo handler repete seu próprio "except Exception as e: return jsonify({"erro": str(e)}), 500", devolvendo a mensagem crua da exceção ao cliente, sem um tratador central de erros.
Impact: Detalhes internos (mensagens de driver, stack trace parcial) vazam para o cliente e o tratamento de erro fica duplicado e inconsistente entre endpoints.
Recommendation: Centralizar o tratamento com @app.errorhandler para exceções genéricas e manter apenas capturas estreitas de exceções de domínio nos handlers (TP-06).

### [MEDIUM] Duplicated Code (AP-14)
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:187-199, models.py:219-231, controllers.py:28-50, controllers.py:72-90
Description: O mapeamento de linha de produto para dicionário é repetido em get_todos_produtos, get_produto_por_id e buscar_produtos; o mapeamento de usuário é repetido em get_todos_usuarios e get_usuario_por_id; o laço que monta a lista de itens de um pedido é repetido quase idêntico em get_pedidos_usuario e get_todos_pedidos; e a validação dos campos obrigatórios de produto é repetida em criar_produto e atualizar_produto.
Impact: Uma correção (ex.: novo campo do produto, nova regra de validação) precisa ser replicada em vários lugares, e as cópias tendem a divergir com o tempo.
Recommendation: Extrair funções únicas de mapeamento linha→dicionário e de validação de produto, reutilizadas por todos os pontos (TP-16).

Deprecated APIs: none detected

### [LOW] Magic Numbers/Strings (AP-17)
File: controllers.py:47, controllers.py:49, controllers.py:52, controllers.py:242, models.py:257-262
Description: Limites e listas de domínio aparecem como literais soltos no código: tamanho mínimo/máximo do nome do produto, lista de categorias válidas e lista de status válidos declaradas inline nos handlers, e os limiares/percentuais de desconto (10000/0.1, 5000/0.05, 1000/0.02) embutidos em relatorio_vendas.
Impact: Mudar um limite de negócio exige localizar e editar cada cópia espalhada pelo código, com risco de inconsistência.
Recommendation: Extrair esses valores para um módulo de constantes/configuração compartilhado (TP-12).

### [LOW] Poor Naming (AP-18)
File: models.py:187, models.py:191, models.py:219, models.py:223
Description: Cursors adicionais recebem nomes numerados sem significado (cursor2, cursor3) em vez de nomes que expressem o que consultam.
Impact: Leitura mais lenta do código e maior chance de confundir qual cursor pertence a qual consulta durante a manutenção.
Recommendation: Renomear para nomes descritivos do que cada consulta representa (TP-17).

### [LOW] Print/Console Logging instead of Logger (AP-19)
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208, controllers.py:209, controllers.py:210, controllers.py:248, controllers.py:250, app.py:56
Description: Eventos de negócio, erros e notificações simuladas (envio de e-mail/SMS/push) são registrados com print() em vez de um logger configurável, inclusive no reset administrativo do banco.
Impact: Sem níveis de log nem destino configurável, a saída vira ruído em produção e pode incluir dados sensíveis em stdout.
Recommendation: Substituir os prints por chamadas a um logger (módulo logging) com o nível apropriado (TP-11).

### [LOW] Unused Imports/Dead Code (AP-20)
File: database.py:2, models.py:2
Description: database.py importa "os" e models.py importa "sqlite3", mas nenhum dos dois módulos é referenciado em nenhum ponto do respectivo arquivo.
Impact: Ruído de leitura e falsa impressão de dependência entre módulos.
Recommendation: Remover os imports não utilizados (TP-18).

================================
Total: 17 findings
================================

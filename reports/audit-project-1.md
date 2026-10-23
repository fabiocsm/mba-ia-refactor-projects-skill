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
Description: A chave de sessão do Flask é um literal versionado ("minha-chave-super-secreta-123") atribuído diretamente a app.config["SECRET_KEY"].
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões/cookies assinados; a troca do segredo exige novo deploy.
Recommendation: Ler o segredo de uma variável de ambiente sem default secreto, gerado em tempo de configuração (TP-01).

### [CRITICAL] SQL Injection by String Building (AP-02)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-161, models.py:163-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-299
Description: Praticamente todas as consultas de models.py são montadas por concatenação de strings com valores vindos de parâmetros/request (ids convertidos com str(), nome/descricao/categoria/email/senha/termo de busca), inclusive a cláusula WHERE dinâmica de buscar_produtos.
Impact: Permite leitura, alteração ou destruição arbitrária dos dados e bypass de autenticação (login_usuario monta a comparação de senha na própria query).
Recommendation: Substituir toda concatenação por placeholders parametrizados do driver sqlite3 (?) em todas as consultas (TP-02).

### [CRITICAL] God Class/God File (AP-03)
File: models.py:133-169, models.py:235-273
Description: models.py concentra, no mesmo módulo, acesso a dados via SQL cru e regras de negócio de múltiplos domínios: criar_pedido valida estoque e calcula o total do pedido (produtos + pedidos + itens_pedido) e relatorio_vendas aplica faixas de desconto sobre o faturamento (pedidos), tudo entrelaçado com as consultas SQL.
Impact: Impossível testar as regras de negócio sem o banco; qualquer mudança de regra obriga a tocar no módulo de dados; responsabilidades indistinguíveis.
Recommendation: Extrair as regras de negócio para uma camada de serviço própria e manter em models.py apenas o acesso a dados (TP-03, TP-04).

### [CRITICAL] Unprotected Administrative/Debug Endpoint (AP-04)
File: app.py:47-57, app.py:59-78
Description: /admin/reset-db apaga todas as tabelas (produtos, usuarios, pedidos, itens_pedido) e /admin/query executa qualquer SQL enviado pelo cliente no corpo da requisição, ambos sem qualquer verificação de autenticação/autorização.
Impact: Qualquer cliente anônimo pode destruir a base de dados ou executar SQL arbitrário (leitura, alteração ou exclusão de qualquer dado).
Recommendation: Proteger as rotas administrativas com credencial lida do ambiente (sem default) exigida antes da ação, ou removê-las do runtime de produção (TP-14).

### [CRITICAL] Plaintext or Weak Password Storage (AP-05)
File: database.py:76-79, models.py:109-111, models.py:122-131
Description: Senhas de usuários (inclusive as de seed) são gravadas e comparadas em texto puro: criar_usuario insere a senha recebida sem hash e login_usuario compara email/senha em texto puro na própria cláusula WHERE.
Impact: O vazamento do arquivo loja.db expõe todas as credenciais em claro, inclusive reutilizadas em outros serviços pelos usuários.
Recommendation: Gerar hash com salt (ex.: werkzeug.security.generate_password_hash) ao criar o usuário e usar generate/check_password_hash no login (TP-09).

### [HIGH] Business Logic in Route Handlers (AP-06)
File: controllers.py:208-210, controllers.py:247-250
Description: criar_pedido e atualizar_status_pedido disparam notificações simuladas (e-mail/SMS/push) e decidem efeitos de negócio por status diretamente no handler da rota, em vez de delegar a uma camada de serviço.
Impact: Regra de negócio (quando e o que notificar) presa ao framework HTTP; impossível reutilizar ou testar sem subir o servidor.
Recommendation: Mover a orquestração de notificações para a camada de serviço, mantendo o handler apenas como adaptador HTTP (TP-04).

### [HIGH] Global Mutable State (AP-07)
File: database.py:4, database.py:8-10
Description: A conexão SQLite é guardada em uma variável global (db_connection) criada sob demanda dentro de get_db() com "global db_connection" e check_same_thread=False, compartilhada entre todas as requisições/threads.
Impact: Condição de corrida entre requisições concorrentes, vazamento de estado entre testes, impossibilidade de isolar a conexão por requisição.
Recommendation: Substituir por conexão criada no composition root e injetada (ou por contexto de aplicação por requisição) (TP-05).

### [HIGH] Sensitive Data Exposure in Responses or Logs (AP-09)
File: models.py:72-87, models.py:89-103, controllers.py:128-134, controllers.py:136-144, controllers.py:276-290
Description: get_todos_usuarios/get_usuario_por_id devolvem o campo "senha" da linha do banco, repassado sem filtro por listar_usuarios/buscar_usuario; health_check devolve "secret_key" e "debug": true na resposta HTTP.
Impact: Vazamento de credenciais de usuários e do segredo de sessão da aplicação para qualquer cliente que chame esses endpoints.
Recommendation: Serializar usuários por allow-list sem o campo senha e remover secret_key/debug da resposta de health check (TP-15, TP-11).

### [HIGH] Debug Mode or Unsafe Defaults Enabled (AP-10)
File: app.py:8, app.py:88
Description: app.config["DEBUG"] = True e app.run(..., debug=True) ligam o modo debug por literal, com bind em host="0.0.0.0".
Impact: O debugger interativo do Werkzeug exposto na rede permite execução remota de código; stack traces vazam detalhes internos.
Recommendation: Ler debug/host de configuração com default seguro (debug=False, 127.0.0.1) (TP-01).

### [MEDIUM] N+1 Queries / Query inside Loop (AP-11)
File: models.py:140, models.py:155, models.py:188, models.py:192, models.py:220, models.py:224
Description: criar_pedido consulta um produto por item dentro do laço (linhas 140 e 155); get_pedidos_usuario e get_todos_pedidos executam uma consulta de itens por pedido e, para cada item, outra consulta do nome do produto, dentro de laços aninhados.
Impact: Número de consultas cresce com o volume de pedidos/itens, gerando latência alta.
Recommendation: Substituir por JOIN/IN (...) que resolva pedidos, itens e produtos em poucas consultas (TP-07).

### [MEDIUM] Missing Input Validation (AP-12)
File: controllers.py:118-121, controllers.py:195-201, models.py:139-146
Description: buscar_produtos converte preco_min/preco_max com float() sem tratar valor inválido; criar_pedido não valida o tipo/formato de cada item de "itens" (produto_id, quantidade) antes de usá-los em comparação e aritmética em models.criar_pedido.
Impact: Entradas malformadas geram erro 500 em vez de uma resposta 400 controlada.
Recommendation: Validar tipo e presença de cada campo (usuario_id, itens[].produto_id, itens[].quantidade, preco_min/preco_max) antes de processar (TP-08).

### [MEDIUM] Scattered or Generic Error Handling (AP-13)
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62, controllers.py:95-96, controllers.py:108-109, controllers.py:125-126, controllers.py:133-134, controllers.py:143-144, controllers.py:164-165, controllers.py:185-186, controllers.py:218-220, controllers.py:226-227, controllers.py:234-235, controllers.py:254-255, controllers.py:261-262, controllers.py:291-292, app.py:77-78
Description: Todo handler repete seu próprio "except Exception as e: return jsonify({"erro": str(e)}), 500", devolvendo a mensagem interna da exceção ao cliente; não há tratador central de erros (@app.errorhandler).
Impact: Detalhes internos (tipo de exceção, mensagens de driver) vazam para o cliente; respostas de erro inconsistentes entre endpoints.
Recommendation: Centralizar o tratamento de erros em um @app.errorhandler e mapear exceções de domínio para status HTTP específicos (TP-06).

### [MEDIUM] Duplicated Code (AP-14)
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:171-201, models.py:203-233, controllers.py:28-54, controllers.py:72-90
Description: O mapeamento de linha para dicionário de produto é repetido em 3 funções de models.py, o de usuário em 2 funções, a montagem de pedido+itens é duplicada entre get_pedidos_usuario e get_todos_pedidos, e o bloco de validação de produto é quase idêntico entre criar_produto e atualizar_produto em controllers.py.
Impact: Correções de formato ou de regra precisam ser replicadas em várias cópias, que tendem a divergir com o tempo.
Recommendation: Extrair funções/serializadores e um validador comuns reutilizados pelos pontos duplicados (TP-16).

Deprecated APIs: none detected

### [LOW] Magic Numbers/Strings (AP-17)
File: models.py:257-262, models.py:247, models.py:250, models.py:253, controllers.py:52, controllers.py:242
Description: Faixas e taxas de desconto (10000, 5000, 1000, 0.1, 0.05, 0.02) estão soltas em relatorio_vendas; as listas de categorias e de status válidos estão declaradas inline nos handlers, e os literais de status ('pendente', 'aprovado', 'cancelado') se repetem entre models.py e controllers.py.
Impact: Mudar um limite de negócio ou um valor válido exige caçar todas as cópias espalhadas pelo código.
Recommendation: Extrair para um módulo de constantes/config compartilhado (TP-12).

### [LOW] Poor Naming (AP-18)
File: models.py:187, models.py:191, models.py:219, models.py:223
Description: Cursores adicionais recebem nomes numerados sem significado (cursor2, cursor3) em get_pedidos_usuario e get_todos_pedidos.
Impact: Leitura mais lenta e maior chance de trocar um cursor pelo outro por engano.
Recommendation: Renomear para nomes que expressem o papel de cada cursor (ex.: cursor_itens, cursor_produto) (TP-17).

### [LOW] Print/Console Logging instead of Logger (AP-19)
File: app.py:56, app.py:84-85, controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:248, controllers.py:250
Description: Eventos, erros e notificações simuladas (inclusive "ENVIANDO EMAIL/SMS/PUSH") são registrados com print() em vez de um logger configurável.
Impact: Sem níveis de log nem destino configurável; ruído em produção e risco de dados sensíveis em stdout.
Recommendation: Substituir por um logger padrão da aplicação (TP-11).

### [LOW] Unused Imports/Dead Code (AP-20)
File: models.py:2, database.py:2
Description: models.py importa sqlite3 e database.py importa os sem que nenhum dos dois módulos seja referenciado no arquivo.
Impact: Ruído de leitura e falsa impressão de dependência direta do driver/sistema.
Recommendation: Remover os imports não utilizados (TP-18).

================================
Total: 17 findings
================================

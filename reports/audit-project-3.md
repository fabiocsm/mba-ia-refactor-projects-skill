================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 6 | LOW: 4

## Findings

### [CRITICAL] Hardcoded Credentials/Secrets (AP-01)
File: app.py:13, services/notification_service.py:9-10
Description: A `SECRET_KEY` do Flask está fixada em texto puro (`'super-secret-key-123'`) em `app.py:13`, e o serviço de notificação guarda usuário e senha de um servidor SMTP real (`taskmanager@gmail.com` / `senha123`) como literais na classe.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de sessão da aplicação e as credenciais do servidor de e-mail; trocar os segredos exige novo deploy.
Recommendation: Ler ambos os valores de variáveis de ambiente sem default secreto (TP-01).

### [CRITICAL] God Class/God File (AP-03)
File: routes/report_routes.py:12-101, routes/report_routes.py:103-155, routes/report_routes.py:157-223
Description: `report_routes.py` concentra, para dois recursos distintos (relatórios e categorias), consultas ORM diretas (`Task.query`, `User.query`, `Category.query`), cálculo de regras de negócio (percentuais, lista de atrasados, produtividade por usuário) e montagem manual da resposta, tudo no mesmo arquivo de rotas.
Impact: Impossível testar o cálculo de relatórios ou o CRUD de categorias isoladamente do framework HTTP; qualquer mudança em uma regra obriga a reler o arquivo inteiro; responsabilidades de dados, negócio e apresentação ficam indistinguíveis.
Recommendation: Extrair a lógica de relatórios para um service dedicado e o CRUD de categorias para seu próprio controller/model, deixando a rota apenas orquestrar (TP-03, TP-04).

### [CRITICAL] Plaintext or Weak Password Storage (AP-05)
File: models/user.py:29, models/user.py:32
Description: `User.set_password` grava a senha com `hashlib.md5(pwd.encode()).hexdigest()` (hash rápido, sem salt) e `check_password` compara repetindo o mesmo MD5.
Impact: Um vazamento do banco permite recuperar as senhas originais por força bruta/rainbow table em segundos, comprometendo contas reutilizadas em outros serviços.
Recommendation: Usar uma KDF de senha com salt (`werkzeug.security.generate_password_hash`/`check_password_hash`) (TP-09).

### [HIGH] Business Logic in Route Handlers (AP-06)
File: routes/task_routes.py:11-63, routes/task_routes.py:65-83, routes/task_routes.py:273-299, routes/user_routes.py:134-151, routes/user_routes.py:153-184, routes/user_routes.py:185-211
Description: Handlers de `tasks` e `users` fazem consulta ORM, calculam regra de negócio (atraso, estatísticas, taxa de conclusão) e serializam a resposta diretamente: `get_tasks`/`get_task` recalculam "overdue" manualmente, `task_stats` agrega contagens e percentuais, `delete_user` orquestra a exclusão em cascata das tasks do usuário, e `login` decide autenticação (checagem de senha, usuário ativo, geração de token) dentro da própria rota.
Impact: Regra de negócio presa ao framework HTTP; impossível reutilizar ou testar sem subir o servidor; qualquer ajuste na regra de atraso ou no fluxo de login exige editar a camada de rotas.
Recommendation: Mover os cálculos e decisões para services/controllers, deixando o handler apenas extrair parâmetros, chamar a camada de negócio e serializar o resultado (TP-04).

### [HIGH] Tight Coupling without Dependency Injection (AP-08)
File: services/notification_service.py:5-10, services/notification_service.py:15-20
Description: `NotificationService.__init__` configura host/porta/usuário/senha do SMTP como literais da própria classe, e `send_email` instancia `smtplib.SMTP(...)` diretamente no corpo do método.
Impact: Impossível substituir o cliente SMTP por um dublê em testes ou trocar de provedor de e-mail sem editar a classe de negócio.
Recommendation: Injetar a configuração e o cliente SMTP (ou uma fábrica) via construtor, montados no composition root (TP-05).

### [HIGH] Sensitive Data Exposure in Responses or Logs (AP-09)
File: models/user.py:16-25, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` inclui o campo `password` (hash) na serialização, e esse dicionário é devolvido ao cliente em `create_user`, `update_user` e `login`.
Impact: O hash da senha de qualquer usuário trafega em respostas HTTP comuns, facilitando ataques offline de força bruta mesmo sem acesso direto ao banco.
Recommendation: Remover `password` da serialização pública (allow-list de campos) (TP-15, TP-11).

### [HIGH] Debug Mode or Unsafe Defaults Enabled (AP-10)
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` liga o debugger interativo do Flask e expõe a aplicação em todas as interfaces de rede por literal fixo.
Impact: O debugger do Werkzeug permite execução remota de código a quem alcançar a porta; stack traces detalhadas vazam para qualquer cliente.
Recommendation: Ler `debug` e `host` de configuração com default seguro (`debug=False`, `127.0.0.1`), habilitando modo de desenvolvimento só por variável de ambiente explícita (TP-01).

### [MEDIUM] N+1 Queries / Query inside Loop (AP-11)
File: routes/task_routes.py:41-57, routes/report_routes.py:53-68, routes/report_routes.py:161-164
Description: `get_tasks` consulta `User`/`Category` dentro do laço sobre as tasks; `summary_report` consulta as tasks de cada usuário dentro de um laço sobre `users`; `get_categories` conta as tasks de cada categoria dentro de um laço sobre `categories`.
Impact: O número de consultas ao banco cresce linearmente com o volume de tasks/usuários/categorias, degradando a latência conforme a base cresce.
Recommendation: Usar eager loading (`joinedload`/`selectinload`) ou `JOIN`/`GROUP BY` para resolver os dados relacionados em uma única consulta (TP-07).

### [MEDIUM] Missing Input Validation (AP-12)
File: routes/task_routes.py:113-114, routes/task_routes.py:182-183, routes/task_routes.py:261, routes/task_routes.py:264, routes/report_routes.py:196-197
Description: `priority` recebido do JSON é comparado (`< 1`, `> 5`) sem checar o tipo em `create_task`/`update_task`; `priority` e `user_id` da query string são convertidos com `int(...)` sem tratar valor inválido em `search_tasks`; `update_category` lê `request.get_json()` e usa `'name' in data` sem verificar se `data` é `None`.
Impact: Uma entrada mal formada (string não numérica, corpo vazio) gera erro 500 não tratado em vez de uma resposta 400 consistente.
Recommendation: Validar tipo e presença dos dados na borda antes de usá-los, devolvendo 400 para entradas inválidas (TP-08).

### [MEDIUM] Scattered or Generic Error Handling (AP-13)
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:151, routes/task_routes.py:204, routes/task_routes.py:221, routes/task_routes.py:236, routes/user_routes.py:87, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221
Description: Praticamente todo handler de escrita tem seu próprio `except:`/`except Exception as e:` genérico devolvendo 500 ou 400, sem nenhum tratador central (`@app.errorhandler`) em `app.py`.
Impact: Respostas de erro inconsistentes entre endpoints equivalentes, risco de vazar detalhes internos em mensagens futuras, e dificuldade para auditar falhas de forma centralizada.
Recommendation: Centralizar o tratamento de erros em handlers de erro do Flask (`@app.errorhandler`) e usar excecões específicas por caso de domínio (TP-06).

### [MEDIUM] Duplicated Code (AP-14)
File: models/task.py:50-60, routes/task_routes.py:17-28, routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:282-287, routes/task_routes.py:296, routes/user_routes.py:162-169, routes/user_routes.py:171-180, routes/report_routes.py:34-43, routes/report_routes.py:67, routes/report_routes.py:132-135, routes/report_routes.py:151
Description: O cálculo de "task atrasada" (due_date no passado e status diferente de done/cancelled) é reimplementado manualmente em cinco handlers diferentes, apesar de existir o método equivalente `Task.is_overdue()` (nunca chamado); a serialização manual de task em dicionário é repetida em `task_routes.py` e `user_routes.py` além do `to_dict()` do model; o cálculo de taxa de conclusão (`done/total*100`) é repetido em três lugares.
Impact: Uma correção na regra de atraso ou no cálculo de percentual precisa ser replicada em todos os pontos, e as cópias já divergem em pequenos detalhes de formatação.
Recommendation: Centralizar cada regra em um único local (model/service) e reutilizá-la em todos os handlers (TP-16).

### [MEDIUM] Deprecated API Usage (AP-15)
File: models/task.py:15-16, models/task.py:52, models/user.py:14, models/category.py:11, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133, utils/helpers.py:38, services/notification_service.py:35, seed.py:66, seed.py:67, seed.py:69, seed.py:70, seed.py:74
Description: `datetime.utcnow()` (e o uso de `datetime.utcnow` como `default`/`onupdate` de coluna) é usado em todo o projeto para gerar timestamps "naive" sem fuso horário.
Impact: Na versão do runtime (Python 3.14.5), `datetime.utcnow()` está deprecada e gera datetimes sem timezone, levando a comparações incorretas quando misturadas com datetimes conscientes de fuso.
Recommendation: Substituir por `datetime.now(timezone.utc)` (TP-10).

### [MEDIUM] Deprecated API Usage (AP-15)
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:213
Description: `Model.query.get(id)` é usado em 16 pontos do projeto para buscar entidades por chave primária.
Impact: `Query.get()` está deprecado desde Flask-SQLAlchemy 3.0/SQLAlchemy 2.0 (declarado no manifesto: `flask-sqlalchemy==3.1.1`), podendo ser removido em versões futuras e gerando avisos de depreciação em runtime.
Recommendation: Substituir por `db.session.get(Model, id)` (TP-10).

### [LOW] Magic Numbers/Strings (AP-17)
File: routes/task_routes.py:96, routes/task_routes.py:99, routes/task_routes.py:113-114, routes/task_routes.py:167, routes/task_routes.py:169, routes/task_routes.py:182-183, models/task.py:46-47, routes/user_routes.py:64, routes/user_routes.py:115, models/category.py:10, routes/report_routes.py:180
Description: Limites de negócio como tamanho do título (`3`/`200`), faixa de prioridade (`1`/`5`), tamanho mínimo de senha (`4`) e cor padrão (`'#000000'`) aparecem como literais repetidos em vários arquivos, apesar de existir um módulo de constantes (`utils/helpers.py`) nunca referenciado por eles.
Impact: Alterar uma regra de negócio (ex.: senha mínima) exige localizar e trocar cada ocorrência manualmente, com risco de deixar alguma desatualizada.
Recommendation: Extrair os literais para constantes nomeadas e reutilizá-las em todos os pontos (TP-12).

### [LOW] Poor Naming (AP-18)
File: routes/report_routes.py:24-28, models/category.py:14, routes/task_routes.py:16, routes/user_routes.py:14, routes/report_routes.py:55, routes/report_routes.py:161
Description: Variáveis numeradas `p1`..`p5` guardam contagens por prioridade sem indicar o que representam; `d` em `Category.to_dict()` é um dicionário de domínio com nome de uma letra; laços usam `t`/`u`/`c` para carregar entidades Task/User/Category inteiras.
Impact: Leitura mais lenta e maior risco de troca acidental entre variáveis parecidas (ex.: `p1` vs `p2`) ao alterar o código.
Recommendation: Renomear para nomes descritivos (`critical_count`, `category_dict`, `task`/`user`/`category`) (TP-17).

### [LOW] Print/Console Logging instead of Logger (AP-19)
File: utils/helpers.py:39, utils/helpers.py:41, routes/user_routes.py:83, routes/user_routes.py:89, routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, services/notification_service.py:21, services/notification_service.py:24
Description: Eventos de negócio e erros (criação/atualização/exclusão de task e usuário, falha ao enviar e-mail) são registrados com `print(...)` em vez de um logger configurável.
Impact: Sem níveis de log nem destino configurável; em produção o volume de `print` gera ruído e pode expor dados em stdout sem controle.
Recommendation: Substituir por um logger (`logging`) com nível apropriado (TP-11).

### [LOW] Unused Imports/Dead Code (AP-20)
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, models/task.py:38-43, models/task.py:45-48, models/task.py:50-60, services/notification_service.py:1-49, utils/helpers.py:19-116
Description: `os`/`sys`/`json`/`time`/`hashlib` são importados e nunca usados nos respectivos arquivos; `format_date`/`calculate_percentage` são importados em `report_routes.py` mas nunca chamados; `Task.validate_status`, `Task.validate_priority` e `Task.is_overdue` nunca são chamados; a classe `NotificationService` nunca é instanciada em nenhum ponto do projeto; e praticamente todo o conteúdo de `utils/helpers.py` (`validate_email`, `sanitize_string`, `generate_id`, `log_action`, `is_valid_color`, `process_task_data` e as constantes `VALID_STATUSES`/`VALID_ROLES`/etc.) não é referenciado por nenhum outro arquivo.
Impact: Ruído que dificulta entender o que de fato está em uso, falsa impressão de que a lógica de notificação e as validações centralizadas já existem, e manutenção de código morto que nunca é executado.
Recommendation: Remover os imports, métodos e módulos não utilizados, ou passar a usá-los no fluxo real (TP-18).

================================
Total: 17 findings
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Hardcoded Credentials/Secrets (AP-01)
File: src/utils.js:2, src/utils.js:3, src/utils.js:4
Description: O objeto `config`, versionado no repositório, grava literais de credenciais de produção: senha de banco (`dbPass: "senha_super_secreta_prod_123"`), usuário de banco (`dbUser: "admin_master"`) e chave de gateway de pagamento com prefixo reconhecível (`paymentGatewayKey: "pk_live_1234567890abcdef"`).
Impact: Qualquer pessoa com acesso ao repositório, a forks ou ao histórico git obtém credenciais de produção; trocar um segredo exige novo deploy.
Recommendation: Ler os segredos de variáveis de ambiente sem default secreto, exclusivamente no composition root (TP-01).

### [CRITICAL] God Class/God File (AP-03)
File: src/AppManager.js:4-141
Description: A classe `AppManager` concentra, no mesmo arquivo, a criação da conexão e do schema (`initDb`), o roteamento HTTP (`setupRoutes` com `app.post`/`app.get`/`app.delete`) e as regras de negócio com acesso a dados via SQL direto para 5 entidades (users, courses, enrollments, payments, audit_logs).
Impact: Impossível testar roteamento, regra de negócio e acesso a dados isoladamente; qualquer alteração em uma entidade arrisca afetar as demais; responsabilidades indistinguíveis.
Recommendation: Separar em camadas MVC — controllers finos, services com a regra de negócio e models com o acesso a dados (TP-03, TP-04).

### [CRITICAL] Unprotected Administrative/Debug Endpoint (AP-04)
File: src/AppManager.js:80
Description: `GET /api/admin/financial-report` está sob prefixo `/admin` e devolve receita agregada e dados de alunos/pagamentos por curso sem qualquer verificação de autenticação ou autorização antes de montar a resposta.
Impact: Qualquer cliente não autenticado lê dados financeiros e pessoais privilegiados da operação.
Recommendation: Exigir credencial/token de administrador lido do ambiente (sem default) antes de processar a rota (TP-14).

### [CRITICAL] Plaintext or Weak Password Storage (AP-05)
File: src/utils.js:17-23, src/AppManager.js:68
Description: `badCrypto` "hasheia" a senha concatenando 10000 vezes um trecho de codificação Base64 reversível (sem salt, sem KDF), e o checkout aplica uma senha padrão literal `"123456"` quando o cliente não envia nenhuma (`badCrypto(p || "123456")`).
Impact: Vazamento do banco expõe (ou permite reverter) todas as senhas armazenadas, inclusive as criadas com a senha padrão previsível.
Recommendation: Substituir por um KDF de senha com salt aleatório (ex.: scrypt/bcrypt) e eliminar a senha padrão implícita (TP-09).

### [HIGH] Global Mutable State (AP-07)
File: src/utils.js:9, src/utils.js:12-15, src/AppManager.js:59
Description: `globalCache` é um objeto de módulo mutado a cada checkout concluído por `logAndCache` (`globalCache[key] = data`), compartilhado entre todas as requisições sem dono explícito nem ciclo de vida definido.
Impact: Vazamento de estado entre requisições concorrentes, condições de corrida e testes interdependentes.
Recommendation: Substituir o cache global por um componente com ciclo de vida definido, criado no composition root e injetado onde necessário (TP-05).

### [HIGH] Tight Coupling without Dependency Injection (AP-08)
File: src/AppManager.js:4-7
Description: `AppManager` instancia sua própria conexão (`this.db = new sqlite3.Database(':memory:')`) dentro do construtor, em vez de recebê-la por injeção.
Impact: Impossível substituir o banco por um dublê em testes unitários; trocar de banco exige editar a mesma classe que contém a regra de negócio.
Recommendation: Criar a conexão no composition root e injetá-la via construtor/parâmetro (TP-05).

### [HIGH] Sensitive Data Exposure in Responses or Logs (AP-09)
File: src/AppManager.js:45
Description: O checkout registra em console o número completo do cartão recebido e a chave do gateway de pagamento (`console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`).
Impact: Dados de cartão (PCI) e segredo de gateway ficam expostos a qualquer leitor dos logs.
Recommendation: Remover o dado sensível do log e, se necessário, registrar apenas identificadores não sensíveis através de um logger central (TP-15, TP-11).

### [MEDIUM] N+1 Queries / Query inside Loop (AP-11)
File: src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106
Description: `GET /api/admin/financial-report` executa uma consulta de matrículas por curso dentro de `courses.forEach` (linha 92) e, para cada matrícula, mais duas consultas (usuário e pagamento) dentro de `enrollments.forEach` (linhas 104 e 106), multiplicando o número de queries pelo volume de dados.
Impact: Latência cresce linearmente com o número de cursos/matrículas; o relatório fica inviável em produção com dados reais.
Recommendation: Substituir os laços por consultas com `JOIN`/`GROUP BY` que tragam os dados agregados em poucas queries (TP-07).

### [MEDIUM] Missing Input Validation (AP-12)
File: src/AppManager.js:29-35, src/AppManager.js:46
Description: Os campos do corpo do checkout (`usr`, `eml`, `pwd`, `c_id`, `card`) só são checados quanto à presença (linha 35), nunca quanto ao tipo; `cc.startsWith("4")` (linha 46) assume que `card` é string e lança excessão não tratada (erro 500) se o cliente enviar outro tipo.
Impact: Entradas malformadas derrubam a requisição com erro 500 em vez de uma resposta 400 controlada.
Recommendation: Validar o tipo de cada campo do corpo antes de usá-lo, com um validador na borda (TP-08).

### [MEDIUM] Scattered or Generic Error Handling (AP-13)
File: src/AppManager.js:41, src/AppManager.js:51, src/AppManager.js:55, src/AppManager.js:70, src/AppManager.js:84, src/AppManager.js:133-136
Description: Cada callback do driver SQLite repete seu próprio `if (err) return res.status(500).send("Erro ...")` com mensagem genérica; em `DELETE /api/users/:id` (linhas 133-136) o `err` do callback é completamente ignorado; não existe middleware central de erro em nenhum ponto da aplicação (`src/app.js`).
Impact: Comportamento de erro inconsistente entre rotas, falhas silenciosas na exclusão de usuário e ausência de um ponto único para padronizar respostas de erro.
Recommendation: Centralizar o tratamento de erro em um middleware do Express e encaminhar falhas com `next(err)` (TP-06).

### [MEDIUM] Callback Hell (AP-16)
File: src/AppManager.js:26-78, src/AppManager.js:80-129
Description: O checkout aninha callbacks em até 5 níveis (`db.get` → `db.get` → `db.run` → `db.run` → `db.run`) e usa `const self = this` (linha 26) para contornar `this` nos callbacks aninhados; o relatório financeiro sincroniza callbacks paralelos de dois laços com contadores manuais (`coursesPending--`, `enrPending--`).
Impact: Fluxo difícil de acompanhar, risco de respostas duplicadas ou nunca enviadas, e erros fáceis de perder entre os níveis de aninhamento.
Recommendation: Reescrever o fluxo com `async`/`await` sobre uma API de banco baseada em Promises (TP-13).

Deprecated APIs: none detected

### [LOW] Magic Numbers/Strings (AP-17)
File: src/AppManager.js:46, src/AppManager.js:108, src/utils.js:19
Description: O literal `"4"` define a regra de aprovação do cartão (linha 46), o literal `'PAID'` é repetido para decidir receita (linha 108) sem constante compartilhada com os demais usos do mesmo status, e o laço de `badCrypto` usa o número mágico `10000` (utils.js:19) sem nenhum significado nomeado.
Impact: Regra de negócio opaca; alterar uma bandeira de cartão, um status ou o custo do hash exige caçar todas as cópias no código.
Recommendation: Extrair os literais de domínio para constantes nomeadas e compartilhadas (TP-12).

### [LOW] Poor Naming (AP-18)
File: src/AppManager.js:29-33, src/utils.js:17
Description: As variáveis `u`, `e`, `p`, `cid` e `cc` carregam, respectivamente, usuário, e-mail, senha, id do curso e número do cartão sem nenhum nome descritivo; a função `badCrypto` nomeia explicitamente um algoritmo ruim em vez de descrever o comportamento que de fato implementa.
Impact: Leitura lenta do fluxo de checkout e risco de interpretar errado o propósito de `badCrypto` ao reutilizá-la.
Recommendation: Renomear para identificadores descritivos de domínio (TP-17).

### [LOW] Print/Console Logging instead of Logger (AP-19)
File: src/app.js:13, src/utils.js:13
Description: O boot da aplicação (`console.log` com a porta, src/app.js:13) e `logAndCache` (`console.log` a cada chave salva no cache, src/utils.js:13) escrevem diretamente em `console.log` em vez de usar um logger configurável.
Impact: Sem níveis de log, sem destino configurável e ruído em produção.
Recommendation: Substituir por um logger central com níveis configuráveis (TP-11).

### [LOW] Unused Imports/Dead Code (AP-20)
File: src/utils.js:10, src/utils.js:25, src/AppManager.js:2
Description: `totalRevenue` é declarado em `utils.js:10`, exportado em `utils.js:25` e importado em `AppManager.js:2`, mas nunca lido nem atribuído em nenhum ponto do projeto.
Impact: Código morto que sugere, de forma falsa, que a receita é acumulada nesse módulo.
Recommendation: Remover a variável, sua exportação e sua importação (TP-18).

================================
Total: 15 findings
================================

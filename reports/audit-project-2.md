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
File: src/utils.js:3, src/utils.js:4
Description: O objeto de configuração versionado traz a senha de banco em texto puro ("senha_super_secreta_prod_123") e a chave do gateway de pagamento com prefixo reconhecível ("pk_live_1234567890abcdef") como literais no código.
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais de produção e a chave do gateway de pagamento; a troca exige novo deploy e o segredo já está no histórico do git.
Recommendation: Mover os valores para variáveis de ambiente sem default secreto e carregar via `process.env` (TP-01).

### [CRITICAL] God Class/God File (AP-03)
File: src/AppManager.js:4-141
Description: A classe AppManager concentra, ao mesmo tempo, a criação da conexão com o banco e do schema (constructor, initDb), o roteamento HTTP (setupRoutes) e as regras de negócio de checkout e de relatório financeiro, todas acessando o SQLite diretamente dentro dos próprios handlers.
Impact: Impossível testar roteamento, regras de negócio e acesso a dados isoladamente; qualquer mudança em uma responsabilidade arrisca afetar as demais; a classe cresce sem limite a cada novo recurso.
Recommendation: Separar em camadas MVC — model(s) para acesso a dados, controllers para orquestração HTTP e services para as regras de negócio (TP-03, TP-04).

### [CRITICAL] Unprotected Administrative/Debug Endpoint (AP-04)
File: src/AppManager.js:80
Description: A rota GET /api/admin/financial-report expõe dados agregados privilegiados (receita por curso, lista de alunos e valores pagos) sob o prefixo /admin sem qualquer verificação de autenticação ou autorização.
Impact: Qualquer cliente não autenticado lê o relatório financeiro completo da plataforma, incluindo receita e dados de alunos.
Recommendation: Exigir credencial/autorização de administrador lida do ambiente antes de executar a rota, desabilitada por padrão (TP-14).

### [CRITICAL] Plaintext or Weak Password Storage (AP-05)
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Description: A função badCrypto "hasheia" a senha repetindo uma codificação base64 reversível 10000 vezes e truncando o resultado — não é um algoritmo de hash com salt. Além disso, o seed grava a senha '123' sem passar por essa função, e o checkout aplica a senha padrão literal "123456" quando o cliente não envia uma.
Impact: Qualquer vazamento do banco expõe efetivamente as senhas em texto reversível; usuários sem senha enviada ficam protegidos por uma senha padrão conhecida.
Recommendation: Substituir por um KDF com salt (bcrypt/scrypt/argon2) e aplicar a mesma função também aos dados de seed, removendo a senha padrão literal (TP-09).

### [HIGH] Global Mutable State (AP-07)
File: src/utils.js:9-10, src/utils.js:14, src/AppManager.js:59
Description: globalCache é um objeto de módulo mutado a cada chamada de logAndCache (chamada pelo checkout a cada requisição), compartilhando estado entre requisições concorrentes sem dono explícito.
Impact: Vazamento de estado entre requisições e condições de corrida sob concorrência; impossível isolar em testes.
Recommendation: Substituir o cache global por um estado com dono explícito, criado no composition root e injetado onde necessário (TP-05).

### [HIGH] Tight Coupling without Dependency Injection (AP-08)
File: src/AppManager.js:2, src/AppManager.js:7, src/AppManager.js:45
Description: AppManager instancia sua própria conexão SQLite no construtor (`new sqlite3.Database(':memory:')`) e lê a configuração global (`config.paymentGatewayKey`) diretamente do módulo utils, em vez de receber essas dependências.
Impact: Impossível substituir o banco ou a configuração por dublês em testes; trocar de banco ou de fonte de configuração exige editar a classe de regras de negócio.
Recommendation: Criar a conexão e a configuração no composition root e injetá-las via construtor (TP-05).

### [HIGH] Sensitive Data Exposure in Responses or Logs (AP-09)
File: src/AppManager.js:45
Description: O log `console.log` do checkout imprime o número completo do cartão informado pelo cliente e a chave do gateway de pagamento a cada requisição.
Impact: Dados de cartão e a chave do gateway de pagamento ficam expostos a qualquer pessoa com acesso aos logs da aplicação.
Recommendation: Remover o log do número do cartão e da chave do gateway; se necessário, registrar apenas um identificador não sensível via um logger central (TP-15, TP-11).

### [MEDIUM] N+1 Queries / Query inside Loop (AP-11)
File: src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106
Description: O relatório financeiro executa uma consulta de matrículas por curso dentro do `forEach` de cursos, e dentro dela uma consulta de usuário e uma de pagamento por matrícula — uma cadeia de N+1 consultas que cresce com o volume de cursos, matrículas e pagamentos.
Impact: O número de consultas ao banco cresce linearmente com o volume de dados, aumentando a latência do relatório proporcionalmente ao catálogo e à base de alunos.
Recommendation: Substituir pelas consultas com JOIN (cursos + matrículas + usuários + pagamentos) em uma única operação (TP-07).

### [MEDIUM] Missing Input Validation (AP-12)
File: src/AppManager.js:29-35, src/AppManager.js:46
Description: O corpo do checkout só é validado com checagem de truthy (`!u || !e || !cid || !cc`), sem verificar o tipo dos campos; `cc.startsWith("4")` assume que `card` é uma string, o que gera erro 500 se o cliente enviar outro tipo (número, objeto, array).
Impact: Entradas com tipos inesperados no corpo da requisição derrubam o handler com erro 500 em vez de uma resposta 400 controlada.
Recommendation: Validar o tipo de cada campo do corpo na borda antes de usá-los (TP-08).

### [MEDIUM] Scattered or Generic Error Handling (AP-13)
File: src/AppManager.js:38, src/AppManager.js:57, src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133
Description: O parâmetro `err` dos callbacks do driver sqlite3 é ignorado em vários pontos (inserção de log de auditoria, consulta de matrículas, de usuário e de pagamento no relatório, exclusão de usuário), e em outro ponto um erro de banco é confundido com "curso não encontrado" (404). Não existe um tratador de erro central no Express.
Impact: Erros de banco silenciados geram respostas de sucesso incorretas (ex.: checkout concluído sem log de auditoria) ou exceções não tratadas; respostas de erro inconsistentes entre rotas.
Recommendation: Verificar e tratar `err` em todo callback e adicionar um middleware de erro central no Express (TP-06).

### [MEDIUM] Callback Hell (AP-16)
File: src/AppManager.js:25-78, src/AppManager.js:83-128
Description: O checkout encadeia seis níveis de callbacks aninhados do driver sqlite3 e usa `const self = this` (linha 26) para contornar `this` nos callbacks; o relatório financeiro aninha três níveis de callbacks e sincroniza as chamadas paralelas com contadores manuais (`coursesPending--`, `enrPending--`).
Impact: Fluxo de controle difícil de acompanhar, alto risco de respostas duplicadas ou nunca enviadas, e erros perdidos nos callbacks não verificados.
Recommendation: Reescrever os fluxos com `async`/`await` sobre uma API baseada em Promises (TP-13).

Deprecated APIs: none detected

### [LOW] Magic Numbers/Strings (AP-17)
File: src/AppManager.js:46, src/AppManager.js:48, src/AppManager.js:108, src/utils.js:19-20, src/utils.js:22
Description: O prefixo "4" do cartão e os literais de status "PAID"/"DENIED" são usados diretamente nas condições de checkout e do relatório; a função badCrypto usa os números mágicos 10000 (iterações), 2 e 10 (tamanhos de substring) sem nomeá-los.
Impact: Regra de negócio e parâmetros do algoritmo ficam opacos; alterar um limite ou status exige caçar cada ocorrência no código.
Recommendation: Extrair para constantes nomeadas (ex.: enum de status de pagamento, constantes de configuração do hashing) (TP-12).

### [LOW] Poor Naming (AP-18)
File: src/AppManager.js:29-33, src/utils.js:17
Description: Os parâmetros do checkout usam abreviações crípticas (`u`, `e`, `p`, `cid`, `cc`) que carregam dado de domínio (usuário, e-mail, senha, id do curso, cartão); a função `badCrypto` já declara no próprio nome que implementa uma criptografia inadequada.
Impact: Leitura mais lenta do fluxo de checkout e risco de troca de parâmetros ao editar o código.
Recommendation: Renomear para nomes de domínio (`username`, `email`, `password`, `courseId`, `cardNumber`) e para um nome que reflita a função real (`hashPassword`) (TP-17).

### [LOW] Print/Console Logging instead of Logger (AP-19)
File: src/app.js:13, src/AppManager.js:45, src/utils.js:13
Description: A aplicação usa `console.log` para registrar o boot do servidor, o processamento do pagamento (incluindo dados sensíveis) e as escritas no cache, sem nenhum logger configurável.
Impact: Sem níveis de log nem destino configurável; ruído em produção e dados sensíveis expostos em stdout.
Recommendation: Introduzir um logger central com níveis configuráveis e usá-lo em vez de `console.log` (TP-11).

### [LOW] Unused Imports/Dead Code (AP-20)
File: src/AppManager.js:2, src/utils.js:2, src/utils.js:5, src/utils.js:10
Description: `totalRevenue` é importado em AppManager.js mas nunca lido; `dbUser` e `smtpUser` são declarados no objeto de configuração mas nenhum outro ponto do projeto os referencia.
Impact: Ruído de código morto e falsa impressão de que esses valores são usados em alguma integração real.
Recommendation: Remover o import e os campos de configuração não utilizados (TP-18).

================================
Total: 15 findings
================================

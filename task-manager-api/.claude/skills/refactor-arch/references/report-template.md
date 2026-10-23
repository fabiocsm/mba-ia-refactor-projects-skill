# Template de Relatório de Auditoria

Área de conhecimento 3. Formato padronizado do relatório da Fase 2. O arquivo gravado em
`reports/audit-project-N.md` tem **exatamente** o mesmo conteúdo impresso no console — do
primeiro `================================` ao último, sem nada antes ou depois.

## Sumário

- [1. Template](#1-template)
- [2. Regras de preenchimento](#2-regras-de-preenchimento)
- [3. Exemplo de finding](#3-exemplo-de-finding)
- [4. Autoverificação antes de imprimir](#4-autoverificação-antes-de-imprimir)

## 1. Template

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <a> | HIGH: <b> | MEDIUM: <c> | LOW: <d>

## Findings

### [CRITICAL] <nome do anti-pattern> (AP-NN)
File: <arquivo>:<linha>[-<linha>][, <arquivo>:<linha>...]
Description: <o que foi encontrado>
Impact: <consequência>
Recommendation: <ação> (TP-NN[, TP-NN])

### [MEDIUM] Deprecated API Usage (AP-15)
File: <arquivo>:<linha>
Description: <API obsoleta usada>
Impact: <consequência>
Recommendation: substituir por <equivalente moderno> (TP-10)

<demais findings MEDIUM>

Deprecated APIs: none detected

### [LOW] <nome do anti-pattern> (AP-NN)
...

================================
Total: <a+b+c+d> findings
================================
```

A linha `Deprecated APIs: none detected` só aparece quando **não** há finding AP-15 e ocupa o
lugar onde ele estaria: depois do último finding MEDIUM e antes do primeiro LOW (sem LOW, logo
antes do separador do `Total`). Os findings LOW continuam depois dela — ela não encerra o
relatório.

## 2. Regras de preenchimento

| Campo | Regra |
|---|---|
| `Project:` | nome exato do diretório do projeto (é usado para resolver `N` em reexecuções) |
| `Stack:` | `<linguagem> + <framework>` como no banner da Fase 1, sem versões |
| `Files:` | `FILES` e `LOC` do `count-source-files.sh` |
| `## Summary` | contagem de findings por severidade; as quatro severidades sempre presentes (use `0`) |
| Título | `### [SEV] <name do catálogo> (AP-NN)`; severidade e nome copiados do catálogo |
| `File:` | caminhos relativos ao diretório do projeto; linha única `arquivo:42` ou faixa `arquivo:10-25`; várias ocorrências separadas por `, `, **repetindo o nome do arquivo em cada uma** (`a.py:10, a.py:42-48, b.py:7` — nunca `a.py:10, 42-48`) |
| `Description:` | português, específico: cita o identificador/trecho encontrado |
| `Impact:` | consequência concreta para segurança, manutenção, testes ou desempenho |
| `Recommendation:` | ação concreta + `TP-NN` do playbook; para AP-15, o equivalente moderno |
| Ordem | todos os CRITICAL, depois HIGH, MEDIUM e LOW; dentro da severidade, pela ordem `AP-NN` |
| `Total` | soma do Summary = número de blocos `### [` |

Outras regras:

- Uma ocorrência conta uma vez; ocorrências do mesmo anti-pattern ficam em um único finding.
- Mínimo esperado em um projeto legado: 5 findings e ao menos 1 CRITICAL ou HIGH. Se a auditoria
  completa encontrar menos, **não invente**: reporte o que existe.
- Nenhum texto fora do bloco (comentários, notas) dentro do relatório.

## 3. Exemplo de finding

Domínio ilustrativo (biblioteca), não relacionado ao projeto auditado:

```text
### [CRITICAL] SQL Injection by String Building (AP-02)
File: storage.py:31, storage.py:58-60, storage.py:112
Description: Consultas de livros e membros montadas com concatenação de valores do request ("SELECT * FROM books WHERE id = " + str(book_id)).
Impact: Permite leitura e alteração arbitrária do banco e bypass da autenticação de membros.
Recommendation: Usar placeholders do driver com parâmetros separados em todas as consultas (TP-02).
```

## 4. Autoverificação antes de imprimir

- [ ] Cada `File:` aponta para linhas que existem e mostram o problema descrito, com o nome do
      arquivo em cada localização.
- [ ] Nenhum finding duplicado para a mesma ocorrência.
- [ ] Ordem CRITICAL → HIGH → MEDIUM → LOW.
- [ ] Summary confere com a contagem de blocos e com o `Total`.
- [ ] Todo `AP-NN` existe no catálogo e todo `TP-NN` no playbook.
- [ ] AP-15 presente com equivalente moderno, ou linha `Deprecated APIs: none detected` no lugar
      dele (após os MEDIUM, antes dos LOW).
- [ ] Todos os findings de todas as severidades presentes (inclusive os LOW após a linha de
      APIs deprecated).
- [ ] Linha `Project:` igual ao nome do diretório.

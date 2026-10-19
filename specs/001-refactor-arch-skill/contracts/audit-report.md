# Contract: relatório de auditoria (`reports/audit-project-N.md`)

Conteúdo do arquivo = bloco impresso na Fase 2, sem edição. Estrutura derivada do exemplo do
enunciado.

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
Description: <o que foi encontrado, em português>
Impact: <consequência>
Recommendation: <ação> (TP-NN)

### [MEDIUM] Deprecated API (AP-NN)
File: <arquivo>:<linha>
Description: <API obsoleta usada>
Impact: <...>
Recommendation: substituir por <equivalente moderno> (TP-NN)

...

================================
Total: <a+b+c+d> findings
================================
```

## Regras verificáveis

| Regra | Verificação |
|---|---|
| Linha `Project:` presente e igual ao diretório | usada na resolução de `N` |
| Ordem CRITICAL → HIGH → MEDIUM → LOW | sequência dos `### [SEV]` |
| `Summary` = contagem dos `### [SEV]` | soma confere com `Total` |
| Cada finding tem `File:`, `Description:`, `Impact:`, `Recommendation:` | grep por bloco |
| Toda localização existe | `sed -n '<linha>p' <arquivo>` mostra o problema |
| ≥ 5 findings e ≥ 1 CRITICAL/HIGH | critérios de aceite |
| Deprecated API: `Recommendation` cita o equivalente moderno | quando presente |
| Nenhuma API deprecated encontrada | linha `Deprecated APIs: none detected` antes de `Total` |

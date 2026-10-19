# Contract: SKILL.md frontmatter e invocação

## Frontmatter (obrigatório)

```yaml
---
name: refactor-arch
description: >-
  <terceira pessoa; caso de uso primeiro; ≤ 1024 caracteres; termos-gatilho: auditoria
  arquitetural, anti-patterns, code smells, severidade, refatoração MVC, validação>
argument-hint: "[report-number]"
disable-model-invocation: true
---
```

| Campo | Regra |
|---|---|
| `name` | exatamente `refactor-arch`; igual ao nome do diretório |
| `description` | ≤ 1024 caracteres; diz o que faz **e** quando usar; terceira pessoa |
| `argument-hint` | documenta o argumento opcional |
| `disable-model-invocation` | `true` (só roda por `/refactor-arch`) |
| campos proibidos sem justificativa no plano | `allowed-tools`, `context`, `agent`, `model`, `effort`, `user-invocable: false` |

## Invocação

| Forma | Comportamento |
|---|---|
| `/refactor-arch` | executa as 3 fases; `N` resolvido automaticamente |
| `/refactor-arch 2` | idem, com `N = 2` para relatório e evidência |
| `/refactor-arch <não numérico>` | argumento ignorado com aviso; `N` automático |

Pré-condição: Claude Code iniciado no diretório do projeto-alvo (research R2).

## Corpo do SKILL.md (estrutura mínima)

1. Objetivo e regras não negociáveis (somente-leitura nas Fases 1–2; pausa obrigatória; falha não
   é remendada).
2. Checklist de progresso copiável (Fases 1, 2, 3).
3. Fase 1 — passos, quando ler `references/project-analysis.md`, saída (banner).
4. Fase 2 — passos, quando ler `references/anti-patterns-catalog.md` e
   `references/report-template.md`, gravação do relatório, pergunta de confirmação.
5. Fase 3 — passos, quando ler `references/mvc-guidelines.md`,
   `references/refactoring-playbook.md` e `references/validation-protocol.md`; sucesso/falha.
6. Tabela de scripts (`${CLAUDE_SKILL_DIR}/scripts/…`) com procedimento manual equivalente.

# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Variáveis de ambiente opcionais (ver `.env.example`): `SECRET_KEY`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`, `DATABASE_PATH`, `ADMIN_TOKEN`.

As rotas `/admin/reset-db` e `/admin/query` exigem o cabeçalho `X-Admin-Token` com o valor de `ADMIN_TOKEN`. Sem essa variável configurada, ambas ficam desabilitadas (403).

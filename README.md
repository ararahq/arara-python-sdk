# Arara Python SDK

[![PyPI](https://img.shields.io/pypi/v/ararahq-sdk)](https://pypi.org/project/ararahq-sdk/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-docs.ararahq.com-orange)](https://docs.ararahq.com)

SDK oficial da [AraraHQ](https://ararahq.com) para Python: envio de WhatsApp, templates, campanhas, contatos, conversas, números, opt-outs, smart links e carteira, com chamadas síncronas e assíncronas.

## Instalação

```bash
pip install ararahq-sdk
```

Requer Python 3.8 ou superior.

## Autenticação

Autenticação por API key (`Bearer ara_live_...`), criada no painel da Arara. Sem chave no construtor, o SDK lê `ARARA_API_KEY`.

```bash
export ARARA_API_KEY="ara_live_..."
```

Algumas áreas exigem chave com permissão **ADMIN**: `contacts`, `conversations`, `wallet` e `auth.me()`. Com chave sem essa permissão a API responde 403 e o SDK levanta `AraraAuthError`.

## Uso rápido

```python
from arara_api_sdk import AraraClient
from arara_api_sdk.models.message import SendMessageRequest

with AraraClient() as client:
    response = client.messages.send(
        SendMessageRequest(
            receiver="+5511987654321",
            template_name="pedido_enviado",
            template_variables=["Ana"],
        ),
        idempotency_key="pedido-4521",
    )
    print(response.id, response.status, response.cost)
```

`receiver` aceita `whatsapp:+5511...`, `+5511...` ou só dígitos. `cost` pode vir `None` (modo TEST, mensagem agendada).

Assíncrono:

```python
import asyncio
from arara_api_sdk import AraraClient
from arara_api_sdk.models.message import SendMessageRequest

async def main():
    async with AraraClient() as client:
        response = await client.messages.send_async(
            SendMessageRequest(receiver="+5511987654321", body="Oi!")
        )
        print(response.id)

asyncio.run(main())
```

## Idempotência e retries

`messages.send`, `messages.send_batch` e `campaigns.create` sempre mandam `Idempotency-Key`. Se você não passar `idempotency_key`, o SDK gera um UUID v4 por chamada e usa a mesma chave em todas as tentativas daquela chamada: um timeout depois de a API aceitar não vira envio duplicado.

Timeout, erro de conexão, 5xx e 429 são repetidos até `max_retries` (backoff exponencial, ou o `Retry-After` do 429). GET, PUT e DELETE repetem livremente; POST e PATCH só repetem quando levam `Idempotency-Key`.

## Recursos

```python
client.auth.me()                                   # GET /auth/me (ADMIN)

client.messages.send(request, idempotency_key=None)
client.messages.send_batch(batch_request)          # até 1000 destinatários
client.messages.get(message_id)
client.messages.list_by_batch(batch_id)

page = client.templates.list(name=None, status=None, page=0, size=50)
page.data, page.pagination.total_pages
client.templates.create(CreateTemplateRequest(name=..., category="UTILITY", body="Olá {{1}}", samples={"1": "Ana"}))
client.templates.get(template_id)                  # sempre pelo id (UUID)
client.templates.get_status(template_id)
client.templates.analytics(template_id, period="30d")
client.templates.delete(template_id)

client.campaigns.create(campaign_request, idempotency_key=None)
client.campaigns.list(page=0, size=20, status=None)   # content, total_pages, total_elements
client.campaigns.get(campaign_id)
client.campaigns.cancel(campaign_id)

client.opt_outs.list()
client.opt_outs.create("+5511987654321", reason="pediu para sair")
client.opt_outs.get("+5511987654321")
client.opt_outs.delete("+5511987654321")

client.smart_links.list(page=0, size=50)           # Page com data e pagination
client.contacts, client.conversations, client.numbers, client.wallet
```

Para achar um template pelo nome, use `client.templates.list(name="...")` e pegue o `id` do resultado.

Todo método tem a versão `_async` (`send_async`, `list_async`, ...).

## Erros

Todo erro herda de `AraraError` e traz `status_code`, `code`, `message`, `details` e `retry_after`, lidos do envelope `{"error": {"code", "message", "details"}}`.

| Situação | Exceção |
|---|---|
| 401, ou 403 sem código (chave inválida, expirada ou sem permissão) | `AraraAuthError` |
| 403 `PLAN_FEATURE_LOCKED` | `AraraPlanFeatureLockedError` (`feature`, `current_plan`, `upgrade_to`) |
| outro 403 com código (`PLAN_LIMIT_REACHED`, `ACCOUNT_NOT_ACTIVATED`...) | `AraraForbiddenError` |
| 400 | `AraraValidationError` |
| 404 | `AraraResourceNotFoundError` |
| 422 (`INVALID_RECIPIENT`, `RECIPIENT_OPTED_OUT`, `TEMPLATE_PAUSED`...) | `AraraUnprocessableError` |
| 429 | `AraraRateLimitError` |
| 5xx | `AraraServerError` |
| timeout / conexão | `AraraTimeoutError` / `AraraConnectionError` |

```python
from arara_api_sdk import AraraPlanFeatureLockedError, AraraUnprocessableError

try:
    client.campaigns.create(request)
except AraraPlanFeatureLockedError as e:
    print(f"Disponível a partir do plano {e.upgrade_to}")
except AraraUnprocessableError as e:
    print(e.code, e.details)
```

## Configuração

```python
client = AraraClient(
    api_key="...",
    timeout=30.0,
    max_retries=3,
    base_url="https://api.ararahq.com",
)
```

Também por variáveis de ambiente: `ARARA_API_KEY`, `ARARA_BASE_URL`, `ARARA_TIMEOUT`, `ARARA_MAX_RETRIES`.

## Desenvolvimento

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]" ruff build
ruff check arara_api_sdk
python -m pytest
python -m build
```

Publicação: cada push na `main` publica no PyPI (Trusted Publishing) se a versão do `pyproject.toml` ainda não existir lá, e cria a tag e o release no GitHub. Ver `CHANGELOG.md`.

## Licença

MIT. Ver `LICENSE`.

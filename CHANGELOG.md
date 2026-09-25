# Changelog

## 2.0.0 - 2026-09-24

Alinha o SDK ao contrato real da API por chave. Versão major porque remove recursos e muda retornos.

### Quebras
- Removidos `payments`, `brain`, `organizations`, `users` e `api_keys`: nenhum deles é alcançável por API key (403 ou rota inexistente).
- `templates.list()` e `smart_links.list()` devolvem `Page` (`data` + `pagination`) em vez de lista; aceitam `page`/`size` (e `name`/`status` em templates).
- `CreateTemplateRequest` manda `body` (obrigatório), `header`, `headerType`, `footer`, `buttons`, `samples`, `variableExamples` e `carouselCards`. `structure_json` saiu (a API ignorava e respondia 400).
- 401 levanta `AraraAuthError`; 403 sem envelope (chave sem permissão, rota fora da allowlist) levanta `AraraForbiddenError`; 403 com código levanta `AraraApiError` (ou `AraraPlanFeatureLockedError` para `PLAN_FEATURE_LOCKED`, com `feature`, `current_plan`, `upgrade_to`); 422 levanta `AraraUnprocessableError`.
- POST/PATCH sem `Idempotency-Key` não são mais repetidos em timeout, erro de conexão, 5xx ou 429.

### Novo
- `auth.me()` (`GET /auth/me`, exige chave ADMIN): `name`, `email`, `role`, `email_pending`.
- `messages.send` e `campaigns.create` sempre enviam `Idempotency-Key`: a do caller (`idempotency_key=`) ou um UUID v4 gerado por chamada e reaproveitado em todos os retries.
- `messages.send_batch` (até 1000 destinatários, resultado por item em `BatchMessageItemResponse`) e `messages.list_by_batch`.
- `campaigns.list`, `campaigns.get`, `campaigns.cancel`; `CampaignRequest` aceita `scheduled_at` e `ab_test`.
- `templates.analytics(id, period)`.
- `opt_outs` (`list`, `create`, `get`, `delete`).
- Todo erro expõe `status_code`, `code`, `message`, `details` e `retry_after`.

### Correções
- `MessageResponse.cost` é opcional (nulo em TEST, agendada ou sem pré-cálculo) e ganhou `reason`. Antes o SDK lançava depois de a API já ter aceitado o envio.
- Resposta 200 sem corpo (ex.: cancelar campanha) devolve `None` em vez de quebrar no parse.
- Configuração e modelos sem APIs obsoletas do pydantic (`class Config`, `Field(env=...)`).

### Publicação
- Publica no PyPI a cada push na `main` via Trusted Publishing quando a versão do `pyproject.toml` ainda não existe, e cria a tag `vX.Y.Z` com release no GitHub.

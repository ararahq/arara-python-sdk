# Arara Python SDK

O SDK oficial da Arara para Python. Esta biblioteca permite integrar facilmente as funcionalidades de mensageria (WhatsApp), gestão de templates, inteligência artificial (Brain), campanhas e pagamentos diretamente no seu aplicativo ou servidor.

---

## 🚀 Destaques (Features)

- **Suporte Nativo a Async/Sync**: Escolha entre operações bloqueantes ou assíncronas (`httpx` baseado).
- **Type Safety**: Utiliza **Pydantic V2** para validação rigorosa de dados e suporte total a autocompletar em IDEs.
- **Resiliência**: Lógica de **Retries** automática com backoff exponencial integrada.
- **Tratamento de Erros Profissional**: Hierarquia de exceções clara para cada status HTTP relevante.
- **Arquitetura Modular**: Recursos organizados por domínio (Messages, Templates, Brain, etc).

---

## 📦 Instalação

```bash
pip install ararahq-sdk
```

> **Nota:** Requer Python 3.8 ou superior.

---

## 🔑 Autenticação

A autenticação é feita via **Bear API Key**. Você pode obter sua chave no painel da Arara.

O SDK busca automaticamente a variável de ambiente `ARARA_API_KEY` caso nenhuma chave seja passada no construtor.

```bash
export ARARA_API_KEY="ara_live_..."
```

---

## 🛠️ Uso Rápido (Quick Start)

### Modo Síncrono (Standard)
Ideal para scripts simples ou servidores que não utilizam async/await.

```python
from arara_api_sdk import AraraClient
from arara_api_sdk.models.message import SendMessageRequest

# O uso de Context Manager garante que os recursos sejam fechados corretamente
with AraraClient(api_key="your_api_key") as client:
    request = SendMessageRequest(
        receiver="5511999999999",
        body="Hello World from Arara SDK!",
        media_url="https://ararahq.com/l/FtFmja" # Opcional: Anexo
    )
    response = client.messages.send(request)
    print(f"Message ID: {response.id} | Status: {response.status}")
```

### Modo Assíncrono (High Performance)
Recomendado para aplicações FastAPI, aiohttp ou volumes massivos de dados.

```python
import asyncio
from arara_api_sdk import AraraClient
from arara_api_sdk.models.message import SendMessageRequest

async def send_bulk():
    async with AraraClient() as client:
        request = SendMessageRequest(
            receiver="5511999999999",
            template_name="welcome_message",
            variables=["Amos"],
            scheduled_at="2024-12-25T10:00:00Z" # Opcional: Agendamento ISO8601
        )
        response = await client.messages.send_async(request)
        print(f"Async Sent: {response.id}")

asyncio.run(send_bulk())
```

---

## 📂 Visão Geral dos Módulos

### 💬 Mensagens (Messages)
Envio de mensagens de texto simples ou baseadas em templates aprovados.
```python
client.messages.send(request)
client.messages.get(message_id)
```

### 📝 Templates
Gestão completa do ciclo de vida de modelos de mensagem do WhatsApp.
```python
client.templates.list()
client.templates.create(create_request)
client.templates.get_status(template_id)
```

### 🧠 AI Brain
Interface direta com o motor de Inteligência Artificial da Arara.
```python
response = client.brain.prompt(BrainRequest(prompt="Como configurar meu webhook?"))
print(response.answer)
```

### 🏢 Organizações & Webhooks
Gestão de membros, números de telefone e configuração de webhooks de recebimento.
```python
webhook = client.organizations.get_webhook()
members = client.organizations.list_members()
```

---

## ⚙️ Configuração Avançada

Você pode customizar o comportamento do HttpClient no momento da inicialização:

```python
client = AraraClient(
    api_key="...",
    timeout=60.0,       # Custom timeout in seconds
    max_retries=5,      # Exponential backoff retries
    base_url="https://..." # Custom API endpoint
)
```

---

## ⚠️ Tratamento de Erros (Error Handling)

O SDK mapeia erros da API para exceções Python específicas:

```python
from arara_api_sdk.exceptions import (
    AraraAuthError, 
    AraraValidationError, 
    AraraResourceNotFoundError
)

try:
    client.messages.send(request)
except AraraAuthError:
    # Error 401
    pass
except AraraResourceNotFoundError:
    # Error 404
    pass
except AraraValidationError as e:
    # Error 400 - Validation details are in e.response_body
    print(e.response_body)
```

---

## 👩‍💻 Desenvolvimento e Testes

Se você deseja contribuir ou rodar os testes localmente:

1. Crie um ambiente virtual: `python -m venv .venv`
2. Ative: `source .venv/bin/activate`
3. Instale as dependências: `pip install -e ".[test]"`
4. Rode os testes: `pytest tests/`

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

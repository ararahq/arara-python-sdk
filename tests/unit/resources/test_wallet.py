import httpx
import pytest

TX = "https://api.arara.test/v1/wallet/transactions"

REAL_PAGE = {
    "content": [
        {
            "id": "tx-1",
            "amount": "-0.05",
            "type": "DEBIT",
            "description": "Mensagem",
            "referenceId": "msg_1",
            "mode": "LIVE",
            "createdAt": "2026-09-24T10:00:00Z",
        }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 1,
    "totalPages": 1,
}


def test_wallet_transactions_parses_real_page_dto(arara_client, respx_mock):
    """Test the WalletTransactionPageDTO body (content, page, size, totals)."""
    route = respx_mock.get(TX).mock(return_value=httpx.Response(200, json=REAL_PAGE))

    page = arara_client.wallet.transactions(page=0, size=20)

    assert page.content[0].reference_id == "msg_1"
    assert page.total_elements == 1
    assert page.page == 0
    assert route.calls[0].request.url.params["size"] == "20"


@pytest.mark.asyncio
async def test_wallet_transactions_async(arara_client, respx_mock):
    """Test the async transactions path."""
    respx_mock.get(TX).mock(return_value=httpx.Response(200, json=REAL_PAGE))

    page = await arara_client.wallet.transactions_async()

    assert page.total_pages == 1

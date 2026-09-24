from typing import List, Optional

from arara_api_sdk.models.message import (
    BatchMessageRequest,
    BatchMessageResponse,
    MessageResponse,
    SendMessageRequest,
)
from arara_api_sdk.resources import BaseResource, idempotency_headers

_MESSAGES = "/v1/messages"
_BATCH = "/v1/messages/batch"


class MessageResource(BaseResource):
    """Resource for sending and reading messages.

    Every send carries an ``Idempotency-Key``. Pass your own to dedupe across
    processes (e.g. your order id); otherwise the SDK generates one per call
    and reuses it on retries.
    """

    def send(
        self, request: SendMessageRequest, idempotency_key: Optional[str] = None
    ) -> MessageResponse:
        """POST /v1/messages — sends a message synchronously."""
        return self._http.request(
            "POST",
            _MESSAGES,
            response_model=MessageResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            headers=idempotency_headers(idempotency_key),
        )

    async def send_async(
        self, request: SendMessageRequest, idempotency_key: Optional[str] = None
    ) -> MessageResponse:
        """POST /v1/messages — sends a message asynchronously."""
        return await self._http.arequest(
            "POST",
            _MESSAGES,
            response_model=MessageResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            headers=idempotency_headers(idempotency_key),
        )

    def send_batch(
        self, request: BatchMessageRequest, idempotency_key: Optional[str] = None
    ) -> BatchMessageResponse:
        """POST /v1/messages/batch — one template to up to 1000 recipients."""
        return self._http.request(
            "POST",
            _BATCH,
            response_model=BatchMessageResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            headers=idempotency_headers(idempotency_key),
        )

    async def send_batch_async(
        self, request: BatchMessageRequest, idempotency_key: Optional[str] = None
    ) -> BatchMessageResponse:
        """POST /v1/messages/batch — asynchronous batch send."""
        return await self._http.arequest(
            "POST",
            _BATCH,
            response_model=BatchMessageResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            headers=idempotency_headers(idempotency_key),
        )

    def get(self, internal_id: str) -> MessageResponse:
        """GET /v1/messages/{id} — message details synchronously."""
        return self._http.request(
            "GET", f"{_MESSAGES}/{internal_id}", response_model=MessageResponse
        )

    async def get_async(self, internal_id: str) -> MessageResponse:
        """GET /v1/messages/{id} — message details asynchronously."""
        return await self._http.arequest(
            "GET", f"{_MESSAGES}/{internal_id}", response_model=MessageResponse
        )

    def list_by_batch(self, batch_id: str) -> List[MessageResponse]:
        """GET /v1/messages?batchId= — every message of a batch."""
        response = self._http.request("GET", _MESSAGES, params={"batchId": batch_id})
        return [MessageResponse.model_validate(item) for item in response]

    async def list_by_batch_async(self, batch_id: str) -> List[MessageResponse]:
        """GET /v1/messages?batchId= — every message of a batch, asynchronously."""
        response = await self._http.arequest(
            "GET", _MESSAGES, params={"batchId": batch_id}
        )
        return [MessageResponse.model_validate(item) for item in response]

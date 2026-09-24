from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field

ItemT = TypeVar("ItemT")


class PaginationInfo(BaseModel):
    """Pagination block of ``{data, pagination}`` responses."""

    model_config = ConfigDict(populate_by_name=True)

    page: int
    size: int
    total_elements: int = Field(..., alias="totalElements")
    total_pages: int = Field(..., alias="totalPages")


class Page(BaseModel, Generic[ItemT]):
    """Paginated response ``{data: [...], pagination: {...}}``."""

    data: List[ItemT]
    pagination: PaginationInfo

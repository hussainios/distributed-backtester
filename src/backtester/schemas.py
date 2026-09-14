from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BacktestRequest(BaseModel):
    strategy: str = Field(min_length=1, max_length=100)
    parameters: dict[str, Any] = Field(default_factory=dict)
    instrument: str = Field(min_length=1, max_length=32)
    start_date: date
    end_date: date
    initial_capital: float = Field(default=100_000, gt=0)
    commission_bps: float = Field(default=1, ge=0)
    slippage_bps: float = Field(default=2, ge=0)

    @model_validator(mode="after")
    def validate_date_range(self) -> "BacktestRequest":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class BacktestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    strategy: str
    parameters: dict[str, Any]
    instrument: str
    start_date: date
    end_date: date
    initial_capital: float
    commission_bps: float
    slippage_bps: float
    status: str
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None


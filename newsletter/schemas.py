from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Seller(BaseModel):
    name: str
    total_price: float


class Digest(BaseModel):
    start_dt: datetime
    end_dt: datetime

    created_leads: int
    closed_leads: int
    total_price: float
    avg_price: float
    conversion: float

    # best_seller: Seller
    # worst_seller: Seller

    alerts: list[
        Literal[
            "Падение по количеству новых сделок",
            "Падение по сумме закрытых сделок",
            "Падение конверсии",
            "Падение среднего чека",
        ]
    ] = Field(default_factory=list)

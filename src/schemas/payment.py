from datetime import datetime

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    payment_method: str = Field(..., description="Payment method")
    amount: float = Field(..., gt=0, description="Payment amount")
    tip_amount: float = Field(0.0, ge=0, description="Tip amount")


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    payment_id: int
    order_id: int
    payment_time: datetime
    status: str

    class Config:
        orm_mode = True

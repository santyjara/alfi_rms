from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    order_type: str = Field(
        ..., description="Type of order (dine-in, takeout, delivery)"
    )
    employee_id: int = Field(..., description="Employee ID who created the order")
    table_id: Optional[int] = Field(None, description="Table ID for dine-in orders")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    order_type: Optional[str] = Field(None, description="Type of order")
    employee_id: Optional[int] = Field(None, description="Employee ID")
    table_id: Optional[int] = Field(None, description="Table ID")
    status: Optional[str] = Field(None, description="Order status")


class OrderResponse(OrderBase):
    order_id: int
    order_time: datetime
    status: str
    subtotal: float
    tax: float
    total: float

    class Config:
        orm_mode = True


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="New status for the order")


# Order Item models
class OrderItemBase(BaseModel):
    menu_item_id: int = Field(..., description="Menu item ID")
    quantity: int = Field(1, gt=0, description="Quantity ordered")
    special_instructions: Optional[str] = Field(
        None, description="Special instructions"
    )


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    order_item_id: int
    order_id: int
    price: float

    class Config:
        orm_mode = True


# Order Item Customization models
class OrderItemCustomizationCreate(BaseModel):
    order_item_id: int = Field(..., description="Order item ID")
    customization_id: int = Field(..., description="Customization ID")


class OrderItemCustomizationResponse(OrderItemCustomizationCreate):
    item_customization_id: int

    class Config:
        orm_mode = True

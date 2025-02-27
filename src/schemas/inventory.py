from typing import Optional

from pydantic import BaseModel, Field


class InventoryItemBase(BaseModel):
    name: str = Field(..., min_length=1, description="Item name")
    quantity: float = Field(..., ge=0, description="Current quantity")
    unit: str = Field(..., description="Unit of measurement")
    cost_per_unit: float = Field(..., gt=0, description="Cost per unit")
    min_threshold: float = Field(
        0.0, ge=0, description="Minimum threshold for reordering"
    )


class InventoryItemCreate(InventoryItemBase):
    supplier_info: Optional[str] = Field(None, description="Supplier information")


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Item name")
    quantity: Optional[float] = Field(None, ge=0, description="Current quantity")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    cost_per_unit: Optional[float] = Field(None, gt=0, description="Cost per unit")
    min_threshold: Optional[float] = Field(
        None, ge=0, description="Minimum threshold for reordering"
    )
    supplier_info: Optional[str] = Field(None, description="Supplier information")


class InventoryItemResponse(InventoryItemBase):
    inventory_item_id: int
    supplier_info: Optional[str]

    class Config:
        orm_mode = True

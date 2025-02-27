from typing import Optional

from pydantic import BaseModel, Field


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    price: float = Field(..., gt=0, description="Item price")
    category: str = Field(..., description="Item category")
    prep_time_minutes: int = Field(15, ge=0, description="Preparation time in minutes")


class MenuItemCreate(MenuItemBase):
    is_available: bool = Field(True, description="Whether the item is available")


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    price: Optional[float] = Field(None, gt=0, description="Item price")
    category: Optional[str] = Field(None, description="Item category")
    prep_time_minutes: Optional[int] = Field(
        None, ge=0, description="Preparation time in minutes"
    )
    is_available: Optional[bool] = Field(
        None, description="Whether the item is available"
    )


class MenuItemResponse(MenuItemBase):
    menu_item_id: int
    is_available: bool

    class Config:
        orm_mode = True


# Menu Item Customization models
class MenuItemCustomizationBase(BaseModel):
    name: str = Field(..., min_length=1, description="Customization name")
    price: float = Field(
        0.0, ge=0, description="Additional price for this customization"
    )


class MenuItemCustomizationCreate(MenuItemCustomizationBase):
    menu_item_id: int = Field(..., description="Menu item ID")
    is_active: bool = Field(True, description="Whether the customization is active")


class MenuItemCustomizationResponse(MenuItemCustomizationBase):
    customization_id: int
    menu_item_id: int
    is_active: bool

    class Config:
        orm_mode = True

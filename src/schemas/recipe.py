from pydantic import BaseModel, Field


class RecipeRequirementCreate(BaseModel):
    menu_item_id: int = Field(..., description="Menu item ID")
    inventory_item_id: int = Field(..., description="Inventory item ID")
    quantity: float = Field(..., gt=0, description="Quantity required")


class RecipeRequirementResponse(RecipeRequirementCreate):
    requirement_id: int

    class Config:
        orm_mode = True

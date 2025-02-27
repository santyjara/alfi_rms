from typing import Optional

from pydantic import BaseModel, Field


class TableBase(BaseModel):
    capacity: int = Field(..., gt=0, description="Table capacity")
    section: str = Field(..., description="Section of the restaurant")


class TableCreate(TableBase):
    status: str = Field("available", description="Table status")
    is_active: bool = Field(True, description="Whether the table is active")


class TableUpdate(BaseModel):
    capacity: Optional[int] = Field(None, gt=0, description="Table capacity")
    section: Optional[str] = Field(None, description="Section of the restaurant")
    status: Optional[str] = Field(None, description="Table status")
    is_active: Optional[bool] = Field(None, description="Whether the table is active")


class TableResponse(TableBase):
    table_id: int
    status: str
    is_active: bool

    class Config:
        orm_mode = True

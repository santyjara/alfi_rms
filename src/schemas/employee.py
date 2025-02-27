from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, description="Employee name")
    role: str = Field(..., description="Employee role")
    contact_info: Optional[str] = Field(None, description="Contact information")


class EmployeeCreate(EmployeeBase):
    credentials: Optional[str] = Field(None, description="Employee credentials")


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Employee name")
    role: Optional[str] = Field(None, description="Employee role")
    contact_info: Optional[str] = Field(None, description="Contact information")
    credentials: Optional[str] = Field(None, description="Employee credentials")
    is_active: Optional[bool] = Field(
        None, description="Whether the employee is active"
    )


class EmployeeResponse(EmployeeBase):
    employee_id: int
    is_active: bool

    class Config:
        orm_mode = True


# Shift models
class ShiftBase(BaseModel):
    employee_id: int = Field(..., description="Employee ID")
    start_time: datetime = Field(..., description="Shift start time")
    end_time: datetime = Field(..., description="Shift end time")
    shift_type: Optional[str] = Field(None, description="Shift type")


class ShiftCreate(ShiftBase):
    pass


class ShiftResponse(ShiftBase):
    shift_id: int

    class Config:
        orm_mode = True

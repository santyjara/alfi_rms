from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReservationBase(BaseModel):
    date_time: datetime = Field(..., description="Date and time of the reservation")
    party_size: int = Field(..., gt=0, description="Number of guests")
    contact_name: str = Field(..., min_length=1, description="Contact name")
    contact_phone: str = Field(..., min_length=5, description="Contact phone number")
    special_requests: Optional[str] = Field(
        None, description="Special requests or notes"
    )


class ReservationCreate(ReservationBase):
    table_id: Optional[int] = Field(None, description="Specific table ID if requested")


class ReservationUpdate(BaseModel):
    date_time: Optional[datetime] = Field(
        None, description="Date and time of the reservation"
    )
    party_size: Optional[int] = Field(None, gt=0, description="Number of guests")
    contact_name: Optional[str] = Field(None, min_length=1, description="Contact name")
    contact_phone: Optional[str] = Field(
        None, min_length=5, description="Contact phone number"
    )
    special_requests: Optional[str] = Field(
        None, description="Special requests or notes"
    )
    status: Optional[str] = Field(None, description="Reservation status")
    table_id: Optional[int] = Field(None, description="Table ID")


class ReservationResponse(ReservationBase):
    reservation_id: int
    status: str
    table_id: int

    class Config:
        orm_mode = True


class ReservationStatusUpdate(BaseModel):
    status: str = Field(..., description="New status for the reservation")

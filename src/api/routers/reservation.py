from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.gateways.database.utils import get_db
from src.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationStatusUpdate,
    ReservationUpdate,
)
from src.services.reservation import ReservationService

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
    responses={404: {"description": "Not found"}},
)


def get_reservation_service(db: Session = Depends(get_db)):
    return ReservationService(db)


@router.post("/", response_model=ReservationResponse, status_code=201)
def create_reservation(
    reservation: ReservationCreate,
    service: ReservationService = Depends(get_reservation_service),
):
    """Create a new reservation."""
    result = service.create_reservation(
        date_time=reservation.date_time,
        party_size=reservation.party_size,
        contact_name=reservation.contact_name,
        contact_phone=reservation.contact_phone,
        special_requests=reservation.special_requests,
        table_id=reservation.table_id,
    )
    if not result:
        raise HTTPException(
            status_code=400, detail="Failed to create reservation. No available tables."
        )
    return result


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int, service: ReservationService = Depends(get_reservation_service)
):
    """Get a reservation by ID."""
    reservation = service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.get("/date/{date}", response_model=List[ReservationResponse])
def get_reservations_by_date(
    date: date, service: ReservationService = Depends(get_reservation_service)
):
    """Get all reservations for a specific date."""
    return service.get_reservations_for_date(date)


@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation: ReservationUpdate,
    service: ReservationService = Depends(get_reservation_service),
):
    """Update a reservation."""
    existing_reservation = service.get_reservation(reservation_id)
    if not existing_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Update only the fields that are not None
    update_data = reservation.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_reservation, key, value)

    service.db.commit()
    return existing_reservation


@router.put("/{reservation_id}/status", response_model=ReservationResponse)
def update_reservation_status(
    reservation_id: int,
    status_update: ReservationStatusUpdate,
    service: ReservationService = Depends(get_reservation_service),
):
    """Update a reservation's status."""
    reservation = service.update_reservation_status(
        reservation_id, status_update.status
    )
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

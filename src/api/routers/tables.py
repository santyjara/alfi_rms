from typing import List, Optional

from db import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from schemas import TableCreate, TableResponse, TableUpdate
from services import TableService

router = APIRouter(
    prefix="/tables",
    tags=["Tables"],
    responses={404: {"description": "Not found"}},
)


def get_table_service(db: Session = Depends(get_db)):
    return TableService(db)


@router.get("/", response_model=List[TableResponse])
def get_tables(
    section: Optional[str] = None,
    status: Optional[str] = None,
    service: TableService = Depends(get_table_service),
):
    """Get all tables, optionally filtered by section and status."""
    return service.get_all_tables(section, status)


@router.get("/available", response_model=List[TableResponse])
def get_available_tables(
    party_size: int = Query(..., description="Size of the party", gt=0),
    service: TableService = Depends(get_table_service),
):
    """Get available tables that can accommodate the party size."""
    return service.get_available_tables(party_size)


@router.get("/{table_id}", response_model=TableResponse)
def get_table(table_id: int, service: TableService = Depends(get_table_service)):
    """Get a table by ID."""
    table = service.get_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.post("/", response_model=TableResponse, status_code=201)
def create_table(
    table: TableCreate, service: TableService = Depends(get_table_service)
):
    """Create a new table."""
    return service.create_table(
        capacity=table.capacity, section=table.section, status=table.status
    )


@router.put("/{table_id}", response_model=TableResponse)
def update_table(
    table_id: int,
    table: TableUpdate,
    service: TableService = Depends(get_table_service),
):
    """Update a table."""
    existing_table = service.get_table(table_id)
    if not existing_table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Update only the fields that are not None
    update_data = table.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_table, key, value)

    service.db.commit()
    return existing_table


@router.put("/{table_id}/status", response_model=TableResponse)
def update_table_status(
    table_id: int,
    status: str = Query(..., description="New status for the table"),
    service: TableService = Depends(get_table_service),
):
    """Update a table's status."""
    table = service.update_table_status(table_id, status)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

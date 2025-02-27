from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from db import get_db
from services import OrderService
from schemas import (
    OrderCreate, OrderUpdate, OrderResponse, OrderStatusUpdate,
    OrderItemCreate, OrderItemResponse, OrderItemCustomizationCreate, OrderItemCustomizationResponse
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)


def get_order_service(db: Session = Depends(get_db)):
    return OrderService(db)


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
        order: OrderCreate,
        service: OrderService = Depends(get_order_service)
):
    """Create a new order."""
    result = service.create_order(
        order_type=order.order_type,
        employee_id=order.employee_id,
        table_id=order.table_id
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create order")
    return result


@router.get("/", response_model=List[OrderResponse])
def get_orders(
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        service: OrderService = Depends(get_order_service)
):
    """Get all orders, optionally filtered by status and type."""
    return service.get_orders(status, order_type)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
        order_id: int,
        service: OrderService = Depends(get_order_service)
):
    """Get an order by ID."""
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
        order_id: int,
        order: OrderUpdate,
        service: OrderService = Depends(get_order_service)
):
    """Update an order."""
    existing_order = service.get_order(order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update only the fields that are not None
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_order, key, value)

    service.db.commit()
    return existing_order


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
        order_id: int,
        status_update: OrderStatusUpdate,
        service: OrderService = Depends(get_order_service)
):
    """Update an order's status."""
    order = service.update_order_status(order_id, status_update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # If status is 'preparing', update inventory
    if status_update.status == 'preparing':
        service.update_inventory_after_order(order_id)

    return order


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=201)
def add_item_to_order(
        order_id: int,
        item: OrderItemCreate,
        service: OrderService = Depends(get_order_service)
):
    """Add an item to an existing order."""
    result = service.add_item_to_order(
        order_id=order_id,
        menu_item_id=item.menu_item_id,
        quantity=item.quantity,
        special_instructions=item.special_instructions
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to add item to order")
    return result


@router.post("/items/{order_item_id}/customizations", response_model=OrderItemCustomizationResponse, status_code=201)
def add_customization_to_order_item(
        order_item_id: int,
        customization: OrderItemCustomizationCreate,
        service: OrderService = Depends(get_order_service)
):
    """Add a customization to an order item."""
    if customization.order_item_id != order_item_id:
        raise HTTPException(status_code=400, detail="Order item ID mismatch")

    result = service.add_customization_to_order_item(
        order_item_id=order_item_id,
        customization_id=customization.customization_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Order item or customization not found")
    return result
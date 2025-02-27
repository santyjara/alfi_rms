from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth.cognito import get_current_user, staff_required

from src.gateways.database.utils import get_db
from src.schemas.menu import (
    MenuItemCreate,
    MenuItemCustomizationCreate,
    MenuItemCustomizationResponse,
    MenuItemResponse,
    MenuItemUpdate,
)
from src.services.menu import MenuService

router = APIRouter(
    prefix="/menu",
    tags=["Menu"],
    responses={404: {"description": "Not found"}},
)


def get_menu_service(db: Session = Depends(get_db)):
    return MenuService(db)


@router.get("/items", response_model=List[MenuItemResponse])
def get_menu_items(
    category: Optional[str] = None,
    available_only: bool = True,
    service: MenuService = Depends(get_menu_service),
):
    """Get menu items, optionally filtered by category and availability."""
    return service.get_menu_items(category, available_only)


@router.get("/items/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(menu_item_id: int, service: MenuService = Depends(get_menu_service)):
    """Get a menu item by ID."""
    menu_item = service.get_menu_item(menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item


@router.post("/items", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    menu_item: MenuItemCreate, 
    current_user: dict = Depends(staff_required),  # Only staff can create items
    service: MenuService = Depends(get_menu_service),
):
    """Create a new menu item (requires staff permissions)."""
    return service.create_menu_item(
        name=menu_item.name,
        price=menu_item.price,
        category=menu_item.category,
        description=menu_item.description,
        prep_time_minutes=menu_item.prep_time_minutes,
        is_available=menu_item.is_available,
    )


@router.put("/items/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(
    menu_item_id: int,
    menu_item: MenuItemUpdate,
    current_user: dict = Depends(staff_required),  # Only staff can update items
    service: MenuService = Depends(get_menu_service),
):
    """Update a menu item."""
    update_data = menu_item.dict(exclude_unset=True)
    result = service.update_menu_item(menu_item_id, **update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return result


@router.post(
    "/items/{menu_item_id}/customizations",
    response_model=MenuItemCustomizationResponse,
    status_code=201,
)
def add_customization_option(
    menu_item_id: int,
    customization: MenuItemCustomizationCreate,
    current_user: dict = Depends(staff_required),  # Only staff can add customizations
    service: MenuService = Depends(get_menu_service),
):
    """Add a customization option to a menu item."""
    if customization.menu_item_id != menu_item_id:
        raise HTTPException(status_code=400, detail="Menu item ID mismatch")

    result = service.add_customization_option(
        menu_item_id=menu_item_id, name=customization.name, price=customization.price
    )
    if not result:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return result

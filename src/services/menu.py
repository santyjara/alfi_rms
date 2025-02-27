import logging

# Import models
from src.gateways.database.models import (
    MenuItem,
    MenuItemCustomization,
)
from src.services.base import BaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MenuService(BaseService):
    def get_menu_items(self, category=None, available_only=True):
        """Get menu items, optionally filtered by category and availability."""
        query = self.db.query(MenuItem)
        if category:
            query = query.filter(MenuItem.category == category)
        if available_only:
            query = query.filter(MenuItem.is_available)
        return query.order_by(MenuItem.category, MenuItem.name).all()

    def get_menu_item(self, menu_item_id):
        """Get a menu item by ID."""
        return self.db.query(MenuItem).get(menu_item_id)

    def create_menu_item(
        self,
        name,
        price,
        category,
        description=None,
        prep_time_minutes=15,
        is_available=True,
    ):
        """Create a new menu item."""
        menu_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category=category,
            prep_time_minutes=prep_time_minutes,
            is_available=is_available,
        )

        self.db.add(menu_item)
        if self.commit_changes():
            return menu_item
        return None

    def update_menu_item(self, menu_item_id, **kwargs):
        """Update a menu item."""
        menu_item = self.get_menu_item(menu_item_id)
        if not menu_item:
            return None

        for key, value in kwargs.items():
            if hasattr(menu_item, key):
                setattr(menu_item, key, value)

        if self.commit_changes():
            return menu_item
        return None

    def add_customization_option(self, menu_item_id, name, price=0.0):
        """Add a customization option to a menu item."""
        menu_item = self.get_menu_item(menu_item_id)
        if not menu_item:
            return None

        customization = MenuItemCustomization(
            menu_item_id=menu_item_id, name=name, price=price, is_active=True
        )

        self.db.add(customization)
        if self.commit_changes():
            return customization
        return None

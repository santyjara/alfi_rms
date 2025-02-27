import logging

# Import models
from src.gateways.database.models import InventoryItem, RecipeRequirement
from src.services.base import BaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InventoryService(BaseService):
    def get_inventory_items(self, low_stock=False):
        """Get all inventory items, optionally filtered for low stock."""
        query = self.db.query(InventoryItem)
        if low_stock:
            query = query.filter(InventoryItem.quantity <= InventoryItem.min_threshold)
        return query.order_by(InventoryItem.name).all()

    def get_inventory_item(self, inventory_item_id):
        """Get an inventory item by ID."""
        return self.db.query(InventoryItem).get(inventory_item_id)

    def update_inventory_levels(self, inventory_item_id, quantity_change):
        """Update inventory levels."""
        inventory_item = self.get_inventory_item(inventory_item_id)
        if not inventory_item:
            return None

        inventory_item.quantity += quantity_change
        if self.commit_changes():
            return inventory_item
        return None

    def create_inventory_item(
        self, name, quantity, unit, cost_per_unit, min_threshold=0.0, supplier_info=None
    ):
        """Create a new inventory item."""
        inventory_item = InventoryItem(
            name=name,
            quantity=quantity,
            unit=unit,
            cost_per_unit=cost_per_unit,
            min_threshold=min_threshold,
            supplier_info=supplier_info,
        )

        self.db.add(inventory_item)
        if self.commit_changes():
            return inventory_item
        return None

    def link_menu_item_to_inventory(self, menu_item_id, inventory_item_id, quantity):
        """Link a menu item to an inventory item with a required quantity."""
        recipe_req = RecipeRequirement(
            menu_item_id=menu_item_id,
            inventory_item_id=inventory_item_id,
            quantity=quantity,
        )

        self.db.add(recipe_req)
        if self.commit_changes():
            return recipe_req
        return None

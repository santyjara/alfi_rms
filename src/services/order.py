import logging
from datetime import datetime

# Import models
from src.gateways.database.models import (MenuItemCustomization, Order,
                                          OrderItem, OrderItemCustomization)
from src.services.base import BaseService
from src.services.inventory import InventoryService
from src.services.menu import MenuService
from src.services.table import TableService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.menu_service = MenuService(db_session)
        self.inventory_service = InventoryService(db_session)
        self.table_service = TableService(db_session)

    def create_order(self, order_type, employee_id, table_id=None):
        """Create a new order."""
        order = Order(
            order_time=datetime.now(),
            order_type=order_type,
            table_id=table_id,
            employee_id=employee_id,
            status="new",
            subtotal=0.00,
            tax=0.00,
            total=0.00,
        )

        self.db.add(order)
        if self.commit_changes():
            return order
        return None

    def get_order(self, order_id):
        """Get an order by ID."""
        return self.db.query(Order).get(order_id)

    def get_orders(self, status=None, order_type=None):
        """Get all orders, optionally filtered by status and type."""
        query = self.db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        return query.all()

    def add_item_to_order(
        self, order_id, menu_item_id, quantity=1, special_instructions=None
    ):
        """Add an item to an existing order."""
        order = self.get_order(order_id)
        menu_item = self.menu_service.get_menu_item(menu_item_id)

        if not order or not menu_item:
            return None

        order_item = OrderItem(
            order_id=order_id,
            menu_item_id=menu_item_id,
            quantity=quantity,
            special_instructions=special_instructions,
            price=menu_item.price,
        )

        self.db.add(order_item)
        if self.commit_changes():
            # Update order totals
            self._calculate_order_totals(order)
            return order_item
        return None

    def _calculate_order_totals(self, order):
        """Calculate and update the subtotal, tax, and total for an order."""
        # This is an internal helper method
        order.subtotal = sum(item.price * item.quantity for item in order.order_items)
        # Get tax rate from config or use default
        tax_rate = 0.0825  # Example: 8.25%
        order.tax = order.subtotal * tax_rate
        order.total = order.subtotal + order.tax
        self.commit_changes()

    def update_order_status(self, order_id, status):
        """Update an order's status."""
        order = self.get_order(order_id)
        if not order:
            return None

        order.status = status

        # If status is 'preparing', update inventory
        if status == "preparing":
            self.update_inventory_after_order(order_id)

        if self.commit_changes():
            return order
        return None

    def update_inventory_after_order(self, order_id):
        """Update inventory levels after an order is placed."""
        order = self.get_order(order_id)
        if not order or order.status != "preparing":
            return False

        success = True
        # For each item in the order
        for order_item in order.order_items:
            menu_item = order_item.menu_item
            # For each ingredient needed for this menu item
            for requirement in menu_item.recipe_requirements:
                # Reduce inventory by quantity required * number of items ordered
                total_required = requirement.quantity * order_item.quantity
                result = self.inventory_service.update_inventory_levels(
                    requirement.inventory_item_id, -total_required
                )
                if not result:
                    success = False

        return success

    def add_customization_to_order_item(self, order_item_id, customization_id):
        """Add a customization to an order item."""
        order_item = self.db.query(OrderItem).get(order_item_id)
        if not order_item:
            return None

        customization = self.db.query(MenuItemCustomization).get(customization_id)
        if not customization:
            return None

        order_item_customization = OrderItemCustomization(
            order_item_id=order_item_id, customization_id=customization_id
        )

        self.db.add(order_item_customization)
        if self.commit_changes():
            # Update the price of the order item to include customization
            order_item.price += customization.price
            self._calculate_order_totals(order_item.order)
            return order_item_customization
        return None

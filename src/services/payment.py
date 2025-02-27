import logging
from datetime import datetime


# Import models
from src.gateways.database.models import (
    Payment
)
from src.services.base import BaseService
from src.services.order import OrderService
from src.services.table import TableService
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaymentService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.order_service = OrderService(db_session)
        self.table_service = TableService(db_session)

    def process_payment(self, order_id, payment_method, amount, tip_amount=0.00):
        """Process a payment for an order."""
        order = self.order_service.get_order(order_id)
        if not order:
            return None

        payment = Payment(
            order_id=order_id,
            payment_time=datetime.now(),
            payment_method=payment_method,
            amount=amount,
            tip_amount=tip_amount,
            status="completed",
        )

        self.db.add(payment)
        order.status = "paid"

        # If it was a dine-in order, free up the table
        if order.table_id and order.order_type == "dine-in":
            self.table_service.update_table_status(order.table_id, "available")

        if self.commit_changes():
            return payment
        return None

    def get_payment(self, payment_id):
        """Get a payment by ID."""
        return self.db.query(Payment).get(payment_id)

    def get_payments_for_order(self, order_id):
        """Get all payments for a specific order."""
        return self.db.query(Payment).filter(Payment.order_id == order_id).all()

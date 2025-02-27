import logging
from datetime import datetime

# Import models
from src.gateways.database.models import Reservation
from src.services.base import BaseService
from src.services.table import TableService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReservationService")


class ReservationService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.table_service = TableService(db_session)

    def create_reservation(
        self,
        date_time,
        party_size,
        contact_name,
        contact_phone,
        special_requests=None,
        table_id=None,
    ):
        """Create a new reservation."""
        if not table_id:
            # Find an available table
            available_tables = self.table_service.get_available_tables(party_size)
            if not available_tables:
                return None
            table_id = available_tables[0].table_id

        reservation = Reservation(
            date_time=date_time,
            party_size=party_size,
            contact_name=contact_name,
            contact_phone=contact_phone,
            special_requests=special_requests,
            table_id=table_id,
            status="confirmed",
        )

        self.db.add(reservation)

        # Update table status
        table = self.table_service.get_table(table_id)
        if table:
            table.status = "reserved"

        if self.commit_changes():
            return reservation
        return None

    def get_reservation(self, reservation_id):
        """Get a reservation by ID."""
        return self.db.query(Reservation).get(reservation_id)

    def get_reservations_for_date(self, date):
        """Get all reservations for a specific date."""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())

        return (
            self.db.query(Reservation)
            .filter(Reservation.date_time.between(start_date, end_date))
            .all()
        )

    def update_reservation_status(self, reservation_id, status):
        """Update a reservation's status."""
        reservation = self.get_reservation(reservation_id)
        if not reservation:
            return None

        reservation.status = status

        # If status is 'seated', update table status
        if status == "seated":
            self.table_service.update_table_status(reservation.table_id, "occupied")

        # If status is 'cancelled', free up the table
        if status in ["cancelled", "no-show"]:
            self.table_service.update_table_status(reservation.table_id, "available")

        if self.commit_changes():
            return reservation
        return None

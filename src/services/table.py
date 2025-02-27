import logging

# Import models
from src.gateways.database.models import Table
from src.services.base import BaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableService(BaseService):
    def get_all_tables(self, section=None, status=None):
        """Get all tables, optionally filtered by section and status."""
        query = self.db.query(Table)
        if section:
            query = query.filter(Table.section == section)
        if status:
            query = query.filter(Table.status == status)
        return query.all()

    def get_available_tables(self, party_size, time=None):
        """Get available tables that can accommodate the party size."""
        query = self.db.query(Table).filter(
            Table.capacity >= party_size,
            Table.status == "available",
            Table.is_active,
        )
        return query.all()

    def get_table(self, table_id):
        """Get a table by ID."""
        return self.db.query(Table).get(table_id)

    def update_table_status(self, table_id, status):
        """Update a table's status."""
        table = self.get_table(table_id)
        if not table:
            return None

        table.status = status
        if self.commit_changes():
            return table
        return None

    def create_table(self, capacity, section, status="available"):
        """Create a new table."""
        table = Table(capacity=capacity, section=section, status=status, is_active=True)

        self.db.add(table)
        if self.commit_changes():
            return table
        return None

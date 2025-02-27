import logging

# Import models
from src.gateways.database.models import Employee, Shift
from src.services.base import BaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmployeeService(BaseService):
    def get_employee(self, employee_id):
        """Get an employee by ID."""
        return self.db.query(Employee).get(employee_id)

    def get_employees(self, role=None, active_only=True):
        """Get all employees, optionally filtered by role and active status."""
        query = self.db.query(Employee)
        if role:
            query = query.filter(Employee.role == role)
        if active_only:
            query = query.filter(Employee.is_active)
        return query.all()

    def create_employee(self, name, role, contact_info=None, credentials=None):
        """Create a new employee."""
        employee = Employee(
            name=name,
            role=role,
            contact_info=contact_info,
            credentials=credentials,
            is_active=True,
        )

        self.db.add(employee)
        if self.commit_changes():
            return employee
        return None

    def update_employee(self, employee_id, **kwargs):
        """Update an employee."""
        employee = self.get_employee(employee_id)
        if not employee:
            return None

        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)

        if self.commit_changes():
            return employee
        return None

    def create_shift(self, employee_id, start_time, end_time, shift_type=None):
        """Create a new shift for an employee."""
        employee = self.get_employee(employee_id)
        if not employee:
            return None

        shift = Shift(
            employee_id=employee_id,
            start_time=start_time,
            end_time=end_time,
            shift_type=shift_type,
        )

        self.db.add(shift)
        if self.commit_changes():
            return shift
        return None

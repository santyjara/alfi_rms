import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Table(Base):
    __tablename__ = "tables"

    table_id = Column(Integer, primary_key=True)
    table_number = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    section = Column(String(50), nullable=False)
    status = Column(String(20), default="available")  # available, reserved, occupied
    is_active = Column(Boolean, default=True)

    # Relationships
    reservations = relationship("Reservation", back_populates="table")
    orders = relationship("Order", back_populates="table")

    def __repr__(self):
        return f"<Table(table_id={self.table_id}, capacity={self.capacity}, section='{self.section}', status='{self.status}')>"


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, nullable=False)
    party_size = Column(Integer, nullable=False)
    contact_name = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    special_requests = Column(Text)
    status = Column(
        String(20), default="confirmed"
    )  # confirmed, seated, cancelled, no-show
    table_id = Column(Integer, ForeignKey("tables.table_id"))

    # Relationships
    table = relationship("Table", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(reservation_id={self.reservation_id}, date_time={self.date_time}, party_size={self.party_size}, status='{self.status}')>"


class MenuItem(Base):
    __tablename__ = "menu_items"

    menu_item_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    prep_time_minutes = Column(Integer, default=15)
    is_available = Column(Boolean, default=True)

    # Relationships
    customizations = relationship("MenuItemCustomization", back_populates="menu_item")
    recipe_requirements = relationship("RecipeRequirement", back_populates="menu_item")
    order_items = relationship("OrderItem", back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem(menu_item_id={self.menu_item_id}, name='{self.name}', price={self.price}, category='{self.category}')>"


class MenuItemCustomization(Base):
    __tablename__ = "menu_item_customizations"

    customization_id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.menu_item_id"))
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), default=0.00)
    is_active = Column(Boolean, default=True)

    # Relationships
    menu_item = relationship("MenuItem", back_populates="customizations")
    order_item_customizations = relationship(
        "OrderItemCustomization", back_populates="customization"
    )

    def __repr__(self):
        return f"<MenuItemCustomization(customization_id={self.customization_id}, name='{self.name}', price={self.price})>"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    inventory_item_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Numeric(10, 2), default=0.00)
    unit = Column(String(20), nullable=False)
    cost_per_unit = Column(Numeric(10, 2), nullable=False)
    min_threshold = Column(Numeric(10, 2), default=0.00)
    supplier_info = Column(Text)

    # Relationships
    recipe_requirements = relationship(
        "RecipeRequirement", back_populates="inventory_item"
    )

    def __repr__(self):
        return f"<InventoryItem(inventory_item_id={self.inventory_item_id}, name='{self.name}', quantity={self.quantity}, unit='{self.unit}')>"


class RecipeRequirement(Base):
    __tablename__ = "recipe_requirements"

    requirement_id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.menu_item_id"))
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.inventory_item_id"))
    quantity = Column(Numeric(10, 2), nullable=False)

    # Relationships
    menu_item = relationship("MenuItem", back_populates="recipe_requirements")
    inventory_item = relationship("InventoryItem", back_populates="recipe_requirements")

    def __repr__(self):
        return f"<RecipeRequirement(requirement_id={self.requirement_id}, menu_item_id={self.menu_item_id}, inventory_item_id={self.inventory_item_id}, quantity={self.quantity})>"


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    contact_info = Column(String(100))
    credentials = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Relationships
    orders = relationship("Order", back_populates="employee")
    shifts = relationship("Shift", back_populates="employee")

    def __repr__(self):
        return f"<Employee(employee_id={self.employee_id}, name='{self.name}', role='{self.role}')>"


class Shift(Base):
    __tablename__ = "shifts"

    shift_id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    shift_type = Column(String(20))  # morning, evening, etc.

    # Relationships
    employee = relationship("Employee", back_populates="shifts")

    def __repr__(self):
        return f"<Shift(shift_id={self.shift_id}, employee_id={self.employee_id}, start_time={self.start_time}, end_time={self.end_time})>"


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    order_time = Column(DateTime, default=datetime.datetime.now)
    order_type = Column(String(20), nullable=False)  # dine-in, takeout, delivery
    table_id = Column(
        Integer, ForeignKey("tables.table_id"), nullable=True
    )  # Nullable for takeout/delivery
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    status = Column(
        String(20), default="new"
    )  # new, preparing, served, paid, cancelled
    subtotal = Column(Numeric(10, 2), default=0.00)
    tax = Column(Numeric(10, 2), default=0.00)
    total = Column(Numeric(10, 2), default=0.00)

    # Relationships
    table = relationship("Table", back_populates="orders")
    employee = relationship("Employee", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments = relationship("Payment", back_populates="order")

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, order_time={self.order_time}, status='{self.status}', total={self.total})>"

    def calculate_totals(self):
        """Calculate and update the subtotal, tax, and total for the order."""
        self.subtotal = sum(item.price * item.quantity for item in self.order_items)
        self.tax = self.subtotal * 0.0825  # Example tax rate of 8.25%
        self.total = self.subtotal + self.tax


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.menu_item_id"))
    quantity = Column(Integer, default=1)
    special_instructions = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)  # Price at time of order

    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    customizations = relationship(
        "OrderItemCustomization",
        back_populates="order_item",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<OrderItem(order_item_id={self.order_item_id}, order_id={self.order_id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})>"


class OrderItemCustomization(Base):
    __tablename__ = "order_item_customizations"

    item_customization_id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey("order_items.order_item_id"))
    customization_id = Column(
        Integer, ForeignKey("menu_item_customizations.customization_id")
    )

    # Relationships
    order_item = relationship("OrderItem", back_populates="customizations")
    customization = relationship(
        "MenuItemCustomization", back_populates="order_item_customizations"
    )

    def __repr__(self):
        return f"<OrderItemCustomization(item_customization_id={self.item_customization_id}, order_item_id={self.order_item_id}, customization_id={self.customization_id})>"


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    payment_time = Column(DateTime, default=datetime.datetime.now)
    payment_method = Column(String(50), nullable=False)  # cash, credit, debit, etc.
    amount = Column(Numeric(10, 2), nullable=False)
    tip_amount = Column(Numeric(10, 2), default=0.00)
    status = Column(String(20), default="completed")  # pending, completed, refunded

    # Relationships
    order = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, order_id={self.order_id}, amount={self.amount}, status='{self.status}')>"


# Database initialization function
def init_db(db_url="sqlite:///restaurant.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

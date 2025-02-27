import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./restaurant.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Get database session dependency
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database function
def init_db():
    from src.gateways.database.models import Base

    Base.metadata.create_all(bind=engine)


# Seed database with initial data
def seed_db():
    db = SessionLocal()

    try:
        from models import Employee, InventoryItem, MenuItem, RecipeRequirement, Table

        # Check if we already have tables
        if db.query(Table).count() == 0:
            # Add some tables
            tables = [
                Table(table_id=1, capacity=2, section="Window", status="available"),
                Table(table_id=2, capacity=2, section="Window", status="available"),
                Table(table_id=3, capacity=4, section="Main", status="available"),
                Table(table_id=4, capacity=4, section="Main", status="available"),
                Table(table_id=5, capacity=6, section="Patio", status="available"),
                Table(table_id=6, capacity=8, section="Private", status="available"),
            ]
            db.add_all(tables)

        # Check if we already have employees
        if db.query(Employee).count() == 0:
            # Add some employees
            employees = [
                Employee(
                    employee_id=1,
                    name="John Doe",
                    role="Manager",
                    contact_info="555-1234",
                    is_active=True,
                ),
                Employee(
                    employee_id=2,
                    name="Jane Smith",
                    role="Server",
                    contact_info="555-5678",
                    is_active=True,
                ),
                Employee(
                    employee_id=3,
                    name="Bob Johnson",
                    role="Chef",
                    contact_info="555-9012",
                    is_active=True,
                ),
            ]
            db.add_all(employees)

        # Check if we already have menu items
        if db.query(MenuItem).count() == 0:
            # Add some menu items
            menu_items = [
                MenuItem(
                    menu_item_id=1,
                    name="Caesar Salad",
                    description="Classic Caesar salad with croutons",
                    price=8.99,
                    category="Appetizers",
                ),
                MenuItem(
                    menu_item_id=2,
                    name="Margherita Pizza",
                    description="Classic pizza with tomato and mozzarella",
                    price=12.99,
                    category="Main",
                ),
                MenuItem(
                    menu_item_id=3,
                    name="Spaghetti Carbonara",
                    description="Pasta with egg, cheese, and bacon",
                    price=14.99,
                    category="Main",
                ),
                MenuItem(
                    menu_item_id=4,
                    name="Chocolate Cake",
                    description="Rich chocolate cake with ganache",
                    price=6.99,
                    category="Desserts",
                ),
                MenuItem(
                    menu_item_id=5,
                    name="Coffee",
                    description="Freshly brewed coffee",
                    price=2.99,
                    category="Beverages",
                ),
            ]
            db.add_all(menu_items)

        # Check if we already have inventory items
        if db.query(InventoryItem).count() == 0:
            # Add some inventory items
            inventory_items = [
                InventoryItem(
                    inventory_item_id=1,
                    name="Lettuce",
                    quantity=20,
                    unit="head",
                    cost_per_unit=1.50,
                    min_threshold=5,
                ),
                InventoryItem(
                    inventory_item_id=2,
                    name="Tomato",
                    quantity=30,
                    unit="kg",
                    cost_per_unit=2.00,
                    min_threshold=5,
                ),
                InventoryItem(
                    inventory_item_id=3,
                    name="Flour",
                    quantity=50,
                    unit="kg",
                    cost_per_unit=1.00,
                    min_threshold=10,
                ),
                InventoryItem(
                    inventory_item_id=4,
                    name="Cheese",
                    quantity=15,
                    unit="kg",
                    cost_per_unit=5.00,
                    min_threshold=3,
                ),
                InventoryItem(
                    inventory_item_id=5,
                    name="Pasta",
                    quantity=25,
                    unit="kg",
                    cost_per_unit=1.50,
                    min_threshold=5,
                ),
                InventoryItem(
                    inventory_item_id=6,
                    name="Chocolate",
                    quantity=10,
                    unit="kg",
                    cost_per_unit=8.00,
                    min_threshold=2,
                ),
                InventoryItem(
                    inventory_item_id=7,
                    name="Coffee Beans",
                    quantity=15,
                    unit="kg",
                    cost_per_unit=12.00,
                    min_threshold=3,
                ),
            ]
            db.add_all(inventory_items)

            # Add recipe requirements (linking menu items to inventory items)
            recipe_requirements = [
                # Caesar Salad requires lettuce
                RecipeRequirement(menu_item_id=1, inventory_item_id=1, quantity=0.5),
                # Margherita Pizza requires flour, tomato, and cheese
                RecipeRequirement(menu_item_id=2, inventory_item_id=3, quantity=0.3),
                RecipeRequirement(menu_item_id=2, inventory_item_id=2, quantity=0.2),
                RecipeRequirement(menu_item_id=2, inventory_item_id=4, quantity=0.25),
                # Spaghetti Carbonara requires pasta and cheese
                RecipeRequirement(menu_item_id=3, inventory_item_id=5, quantity=0.2),
                RecipeRequirement(menu_item_id=3, inventory_item_id=4, quantity=0.1),
                # Chocolate Cake requires flour and chocolate
                RecipeRequirement(menu_item_id=4, inventory_item_id=3, quantity=0.15),
                RecipeRequirement(menu_item_id=4, inventory_item_id=6, quantity=0.1),
                # Coffee requires coffee beans
                RecipeRequirement(menu_item_id=5, inventory_item_id=7, quantity=0.02),
            ]
            db.add_all(recipe_requirements)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
    finally:
        db.close()


# Call this on startup
def startup_db_handler():
    """Initialize and seed the database on app startup."""
    init_db()
    seed_db()

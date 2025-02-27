# api/seed.py
import os
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from src.gateways.database.models import (
    Base,
    Employee,
    InventoryItem,
    MenuItem,
    MenuItemCustomization,
    Order,
    OrderItem,
    OrderItemCustomization,
    Payment,
    RecipeRequirement,
    Reservation,
    Shift,
    Table,
)
from src.gateways.database.utils import SessionLocal, engine


def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Only seed if tables are empty
        if db.query(Table).count() == 0:
            print("Seeding tables...")
            seed_tables(db)

        if db.query(Employee).count() == 0:
            print("Seeding employees...")
            seed_employees(db)

        if db.query(MenuItem).count() == 0:
            print("Seeding menu items...")
            seed_menu_items(db)

        if db.query(InventoryItem).count() == 0:
            print("Seeding inventory items...")
            seed_inventory(db)

        if db.query(Reservation).count() == 0:
            print("Seeding reservations...")
            seed_reservations(db)

        if db.query(Order).count() == 0:
            print("Seeding orders...")
            seed_orders(db)

        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_tables(db: Session):
    tables = [
        Table(capacity=2, section="Window", status="available"),
        Table(capacity=2, section="Window", status="available"),
        Table(capacity=4, section="Main", status="available"),
        Table(capacity=4, section="Main", status="available"),
        Table(capacity=6, section="Main", status="available"),
        Table(capacity=6, section="Patio", status="available"),
        Table(capacity=8, section="Private", status="available"),
        Table(capacity=10, section="Private", status="available"),
    ]
    db.add_all(tables)
    db.commit()
    return tables


def seed_employees(db: Session):
    employees = [
        Employee(
            name="John Smith",
            role="Manager",
            contact_info="555-1234",
            credentials="admin",
            is_active=True,
        ),
        Employee(
            name="Emily Johnson",
            role="Host",
            contact_info="555-2345",
            credentials="host",
            is_active=True,
        ),
        Employee(
            name="Michael Brown",
            role="Server",
            contact_info="555-3456",
            credentials="server",
            is_active=True,
        ),
        Employee(
            name="Jessica Davis",
            role="Server",
            contact_info="555-4567",
            credentials="server",
            is_active=True,
        ),
        Employee(
            name="David Wilson",
            role="Chef",
            contact_info="555-5678",
            credentials="kitchen",
            is_active=True,
        ),
        Employee(
            name="Sarah Martinez",
            role="Chef",
            contact_info="555-6789",
            credentials="kitchen",
            is_active=True,
        ),
        Employee(
            name="Robert Taylor",
            role="Bartender",
            contact_info="555-7890",
            credentials="bar",
            is_active=True,
        ),
    ]
    db.add_all(employees)
    db.commit()

    # Add some shifts
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    morning_shift_start = today.replace(hour=10, minute=0)
    morning_shift_end = today.replace(hour=16, minute=0)
    evening_shift_start = today.replace(hour=16, minute=0)
    evening_shift_end = today.replace(hour=23, minute=0)

    shifts = []
    # Add shifts for a week
    for day_offset in range(7):
        # day = today + timedelta(days=day_offset)
        morning_start = morning_shift_start + timedelta(days=day_offset)
        morning_end = morning_shift_end + timedelta(days=day_offset)
        evening_start = evening_shift_start + timedelta(days=day_offset)
        evening_end = evening_shift_end + timedelta(days=day_offset)

        # Assign different employees to different shifts
        for employee in employees:
            # Skip some days randomly
            if random.random() < 0.3:
                continue

            # Assign to morning or evening shift
            if random.random() < 0.5:
                shifts.append(
                    Shift(
                        employee_id=employee.employee_id,
                        start_time=morning_start,
                        end_time=morning_end,
                        shift_type="morning",
                    )
                )
            else:
                shifts.append(
                    Shift(
                        employee_id=employee.employee_id,
                        start_time=evening_start,
                        end_time=evening_end,
                        shift_type="evening",
                    )
                )

    db.add_all(shifts)
    db.commit()
    return employees


def seed_menu_items(db: Session):
    menu_items = [
        # Appetizers
        MenuItem(
            name="Caesar Salad",
            description="Fresh romaine lettuce with Caesar dressing, croutons, and parmesan",
            price=8.99,
            category="Appetizers",
        ),
        MenuItem(
            name="Bruschetta",
            description="Toasted bread topped with diced tomatoes, garlic, basil, and olive oil",
            price=7.99,
            category="Appetizers",
        ),
        MenuItem(
            name="Calamari",
            description="Lightly fried squid served with marinara sauce",
            price=11.99,
            category="Appetizers",
        ),
        MenuItem(
            name="Mozzarella Sticks",
            description="Breaded and fried mozzarella served with marinara sauce",
            price=8.99,
            category="Appetizers",
        ),
        # Main Courses
        MenuItem(
            name="Margherita Pizza",
            description="Classic pizza with fresh tomato sauce, mozzarella, and basil",
            price=13.99,
            category="Main",
        ),
        MenuItem(
            name="Pepperoni Pizza",
            description="Pizza with tomato sauce, mozzarella, and pepperoni",
            price=15.99,
            category="Main",
        ),
        MenuItem(
            name="Spaghetti Carbonara",
            description="Pasta with eggs, cheese, pancetta, and black pepper",
            price=14.99,
            category="Main",
        ),
        MenuItem(
            name="Lasagna",
            description="Layered pasta with meat sauce, ricotta, and mozzarella",
            price=16.99,
            category="Main",
        ),
        MenuItem(
            name="Chicken Parmesan",
            description="Breaded chicken breast topped with marinara sauce and mozzarella",
            price=17.99,
            category="Main",
        ),
        MenuItem(
            name="Grilled Salmon",
            description="Salmon fillet grilled with lemon and herbs",
            price=19.99,
            category="Main",
        ),
        # Desserts
        MenuItem(
            name="Tiramisu",
            description="Classic Italian dessert with coffee-soaked ladyfingers and mascarpone",
            price=7.99,
            category="Desserts",
        ),
        MenuItem(
            name="Chocolate Cake",
            description="Rich chocolate cake with ganache",
            price=6.99,
            category="Desserts",
        ),
        MenuItem(
            name="Cheesecake",
            description="New York style cheesecake with berry compote",
            price=7.99,
            category="Desserts",
        ),
        # Beverages
        MenuItem(
            name="Soda", description="Assorted sodas", price=2.99, category="Beverages"
        ),
        MenuItem(
            name="Iced Tea",
            description="Freshly brewed iced tea",
            price=2.99,
            category="Beverages",
        ),
        MenuItem(
            name="Coffee",
            description="Regular or decaf",
            price=2.99,
            category="Beverages",
        ),
        MenuItem(
            name="Glass of Wine",
            description="House red or white wine",
            price=7.99,
            category="Beverages",
        ),
    ]
    db.add_all(menu_items)
    db.commit()

    # Add customizations
    customizations = [
        # Pizza customizations
        MenuItemCustomization(
            menu_item_id=5, name="Extra Cheese", price=1.50, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=5, name="Mushrooms", price=1.00, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=5, name="Olives", price=1.00, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=6, name="Extra Pepperoni", price=1.50, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=6, name="Mushrooms", price=1.00, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=6, name="Olives", price=1.00, is_active=True
        ),
        # Pasta customizations
        MenuItemCustomization(
            menu_item_id=7, name="Gluten-Free Pasta", price=2.00, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=7, name="Extra Cheese", price=1.50, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=8, name="Extra Cheese", price=1.50, is_active=True
        ),
        # Beverage customizations
        MenuItemCustomization(
            menu_item_id=16, name="Almond Milk", price=0.50, is_active=True
        ),
        MenuItemCustomization(
            menu_item_id=16, name="Extra Shot", price=1.00, is_active=True
        ),
    ]
    db.add_all(customizations)
    db.commit()

    return menu_items


def seed_inventory(db: Session):
    inventory_items = [
        InventoryItem(
            name="Lettuce",
            quantity=30,
            unit="head",
            cost_per_unit=1.50,
            min_threshold=5,
        ),
        InventoryItem(
            name="Tomato", quantity=50, unit="kg", cost_per_unit=2.00, min_threshold=10
        ),
        InventoryItem(
            name="Flour", quantity=100, unit="kg", cost_per_unit=1.00, min_threshold=20
        ),
        InventoryItem(
            name="Cheese", quantity=30, unit="kg", cost_per_unit=5.00, min_threshold=5
        ),
        InventoryItem(
            name="Pasta", quantity=40, unit="kg", cost_per_unit=1.50, min_threshold=10
        ),
        InventoryItem(
            name="Chicken", quantity=25, unit="kg", cost_per_unit=4.00, min_threshold=5
        ),
        InventoryItem(
            name="Beef", quantity=20, unit="kg", cost_per_unit=6.00, min_threshold=5
        ),
        InventoryItem(
            name="Salmon", quantity=15, unit="kg", cost_per_unit=8.00, min_threshold=3
        ),
        InventoryItem(
            name="Olive Oil",
            quantity=20,
            unit="liter",
            cost_per_unit=10.00,
            min_threshold=5,
        ),
        InventoryItem(
            name="Coffee Beans",
            quantity=15,
            unit="kg",
            cost_per_unit=12.00,
            min_threshold=3,
        ),
        InventoryItem(
            name="Wine",
            quantity=30,
            unit="bottle",
            cost_per_unit=15.00,
            min_threshold=10,
        ),
        InventoryItem(
            name="Soda",
            quantity=100,
            unit="liter",
            cost_per_unit=1.00,
            min_threshold=20,
        ),
    ]
    db.add_all(inventory_items)
    db.commit()

    # Link inventory to menu items with recipe requirements
    menu_items = db.query(MenuItem).all()

    # A dictionary to map menu item name to its ID
    menu_item_map = {item.name: item.menu_item_id for item in menu_items}

    # A dictionary to map inventory item name to its ID
    inventory_map = {item.name: item.inventory_item_id for item in inventory_items}

    recipe_requirements = [
        # Caesar Salad
        RecipeRequirement(
            menu_item_id=menu_item_map["Caesar Salad"],
            inventory_item_id=inventory_map["Lettuce"],
            quantity=0.5,
        ),
        # Margherita Pizza
        RecipeRequirement(
            menu_item_id=menu_item_map["Margherita Pizza"],
            inventory_item_id=inventory_map["Flour"],
            quantity=0.3,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Margherita Pizza"],
            inventory_item_id=inventory_map["Tomato"],
            quantity=0.2,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Margherita Pizza"],
            inventory_item_id=inventory_map["Cheese"],
            quantity=0.25,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Margherita Pizza"],
            inventory_item_id=inventory_map["Olive Oil"],
            quantity=0.05,
        ),
        # Pepperoni Pizza
        RecipeRequirement(
            menu_item_id=menu_item_map["Pepperoni Pizza"],
            inventory_item_id=inventory_map["Flour"],
            quantity=0.3,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Pepperoni Pizza"],
            inventory_item_id=inventory_map["Tomato"],
            quantity=0.2,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Pepperoni Pizza"],
            inventory_item_id=inventory_map["Cheese"],
            quantity=0.3,
        ),
        # Spaghetti Carbonara
        RecipeRequirement(
            menu_item_id=menu_item_map["Spaghetti Carbonara"],
            inventory_item_id=inventory_map["Pasta"],
            quantity=0.2,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Spaghetti Carbonara"],
            inventory_item_id=inventory_map["Cheese"],
            quantity=0.1,
        ),
        # Grilled Salmon
        RecipeRequirement(
            menu_item_id=menu_item_map["Grilled Salmon"],
            inventory_item_id=inventory_map["Salmon"],
            quantity=0.25,
        ),
        RecipeRequirement(
            menu_item_id=menu_item_map["Grilled Salmon"],
            inventory_item_id=inventory_map["Olive Oil"],
            quantity=0.05,
        ),
        # Coffee
        RecipeRequirement(
            menu_item_id=menu_item_map["Coffee"],
            inventory_item_id=inventory_map["Coffee Beans"],
            quantity=0.02,
        ),
        # Wine
        RecipeRequirement(
            menu_item_id=menu_item_map["Glass of Wine"],
            inventory_item_id=inventory_map["Wine"],
            quantity=0.20,
        ),
        # Soda
        RecipeRequirement(
            menu_item_id=menu_item_map["Soda"],
            inventory_item_id=inventory_map["Soda"],
            quantity=0.3,
        ),
    ]
    db.add_all(recipe_requirements)
    db.commit()

    return inventory_items


def seed_reservations(db: Session):
    tables = db.query(Table).all()

    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    reservations = []
    # Create reservations for the next 7 days
    for day_offset in range(7):
        reservation_date = today + timedelta(days=day_offset)

        # Lunch reservations (between 11:00 and 14:00)
        for hour in range(11, 14):
            for _ in range(random.randint(1, 3)):  # 1-3 reservations per hour
                table = random.choice(tables)
                minute = random.choice([0, 15, 30, 45])
                reservation_time = reservation_date.replace(hour=hour, minute=minute)

                # Only add future reservations
                if reservation_time > now:
                    reservations.append(
                        Reservation(
                            date_time=reservation_time,
                            party_size=random.randint(1, table.capacity),
                            contact_name=f"Customer {len(reservations) + 1}",
                            contact_phone=f"555-{random.randint(1000, 9999)}",
                            special_requests=random.choice(
                                [
                                    "No special requests",
                                    "Window seat preferred",
                                    "Highchair needed",
                                    "",
                                ]
                            ),
                            table_id=table.table_id,
                            status="confirmed",
                        )
                    )

        # Dinner reservations (between 17:00 and 21:00)
        for hour in range(17, 22):
            for _ in range(random.randint(2, 4)):  # 2-4 reservations per hour
                table = random.choice(tables)
                minute = random.choice([0, 15, 30, 45])
                reservation_time = reservation_date.replace(hour=hour, minute=minute)

                # Only add future reservations
                if reservation_time > now:
                    reservations.append(
                        Reservation(
                            date_time=reservation_time,
                            party_size=random.randint(1, table.capacity),
                            contact_name=f"Customer {len(reservations) + 1}",
                            contact_phone=f"555-{random.randint(1000, 9999)}",
                            special_requests=random.choice(
                                [
                                    "No special requests",
                                    "Window seat preferred",
                                    "Highchair needed",
                                    "",
                                ]
                            ),
                            table_id=table.table_id,
                            status="confirmed",
                        )
                    )

    db.add_all(reservations)
    db.commit()
    return reservations


def seed_orders(db: Session):
    employees = db.query(Employee).filter(Employee.role == "Server").all()
    tables = db.query(Table).all()
    menu_items = db.query(MenuItem).all()
    customizations = db.query(MenuItemCustomization).all()

    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    orders = []
    # Create orders for the past 7 days (historical data)
    for day_offset in range(-7, 0):
        order_date = today + timedelta(days=day_offset)

        # Create some lunch orders
        for _ in range(random.randint(5, 10)):
            employee = random.choice(employees)
            table = random.choice(tables)
            order_time = order_date.replace(
                hour=random.randint(11, 14), minute=random.randint(0, 59)
            )

            order = Order(
                order_time=order_time,
                order_type="dine-in",
                table_id=table.table_id,
                employee_id=employee.employee_id,
                status="paid",
                subtotal=0.00,
                tax=0.00,
                total=0.00,
            )
            db.add(order)
            db.flush()  # To get the order_id

            # Add random items to the order
            for _ in range(random.randint(1, 4)):
                menu_item = random.choice(menu_items)
                quantity = random.randint(1, 2)

                order_item = OrderItem(
                    order_id=order.order_id,
                    menu_item_id=menu_item.menu_item_id,
                    quantity=quantity,
                    special_instructions=random.choice(["", "Extra hot", "No onions"]),
                    price=menu_item.price,
                )
                db.add(order_item)
                db.flush()  # To get the order_item_id

                # Maybe add a customization
                if random.random() < 0.3:
                    # Get customizations for this menu item
                    item_customizations = [
                        c
                        for c in customizations
                        if c.menu_item_id == menu_item.menu_item_id
                    ]
                    if item_customizations:
                        customization = random.choice(item_customizations)
                        db.add(
                            OrderItemCustomization(
                                order_item_id=order_item.order_item_id,
                                customization_id=customization.customization_id,
                            )
                        )

            # Calculate totals
            order_items = (
                db.query(OrderItem).filter(OrderItem.order_id == order.order_id).all()
            )
            subtotal = sum(item.price * item.quantity for item in order_items)
            tax = subtotal * Decimal("0.0825")  # 8.25% tax
            total = subtotal + tax

            order.subtotal = subtotal
            order.tax = tax
            order.total = total

            # Add payment
            payment = Payment(
                order_id=order.order_id,
                payment_time=order_time + timedelta(minutes=random.randint(45, 90)),
                payment_method=random.choice(["cash", "credit", "debit"]),
                amount=total,
                tip_amount=subtotal * Decimal(random.uniform(0.15, 0.25)),  # 15-25% tip
                status="completed",
            )
            db.add(payment)

            orders.append(order)

        # Create some dinner orders
        for _ in range(random.randint(8, 15)):
            employee = random.choice(employees)
            table = random.choice(tables)
            order_time = order_date.replace(
                hour=random.randint(17, 21), minute=random.randint(0, 59)
            )

            order = Order(
                order_time=order_time,
                order_type="dine-in",
                table_id=table.table_id,
                employee_id=employee.employee_id,
                status="paid",
                subtotal=0.00,
                tax=0.00,
                total=0.00,
            )
            db.add(order)
            db.flush()  # To get the order_id

            # Add random items to the order
            for _ in range(random.randint(2, 6)):
                menu_item = random.choice(menu_items)
                quantity = random.randint(1, 2)

                order_item = OrderItem(
                    order_id=order.order_id,
                    menu_item_id=menu_item.menu_item_id,
                    quantity=quantity,
                    special_instructions=random.choice(["", "Extra hot", "No onions"]),
                    price=menu_item.price,
                )
                db.add(order_item)
                db.flush()  # To get the order_item_id

                # Maybe add a customization
                if random.random() < 0.3:
                    # Get customizations for this menu item
                    item_customizations = [
                        c
                        for c in customizations
                        if c.menu_item_id == menu_item.menu_item_id
                    ]
                    if item_customizations:
                        customization = random.choice(item_customizations)
                        db.add(
                            OrderItemCustomization(
                                order_item_id=order_item.order_item_id,
                                customization_id=customization.customization_id,
                            )
                        )

            # Calculate totals
            order_items = (
                db.query(OrderItem).filter(OrderItem.order_id == order.order_id).all()
            )
            subtotal = sum(item.price * item.quantity for item in order_items)
            tax = subtotal * Decimal("0.0825")  # 8.25% tax
            total = subtotal + tax

            order.subtotal = subtotal
            order.tax = tax
            order.total = total

            # Add payment
            payment = Payment(
                order_id=order.order_id,
                payment_time=order_time + timedelta(minutes=random.randint(45, 120)),
                payment_method=random.choice(["cash", "credit", "debit"]),
                amount=total,
                tip_amount=subtotal * Decimal(random.uniform(0.15, 0.25)),  # 15-25% tip
                status="completed",
            )
            db.add(payment)

            orders.append(order)

    # Create a few active orders for today
    for _ in range(random.randint(2, 5)):
        employee = random.choice(employees)
        table = random.choice(tables)
        order_time = now - timedelta(minutes=random.randint(15, 60))

        order = Order(
            order_time=order_time,
            order_type="dine-in",
            table_id=table.table_id,
            employee_id=employee.employee_id,
            status=random.choice(["new", "preparing", "served"]),
            subtotal=0.00,
            tax=0.00,
            total=0.00,
        )
        db.add(order)
        db.flush()  # To get the order_id

        # Add random items to the order
        for _ in range(random.randint(2, 4)):
            menu_item = random.choice(menu_items)
            quantity = random.randint(1, 2)

            order_item = OrderItem(
                order_id=order.order_id,
                menu_item_id=menu_item.menu_item_id,
                quantity=quantity,
                special_instructions=random.choice(["", "Extra hot", "No onions"]),
                price=menu_item.price,
            )
            db.add(order_item)
            db.flush()  # To get the order_item_id

            # Maybe add a customization
            if random.random() < 0.3:
                # Get customizations for this menu item
                item_customizations = [
                    c
                    for c in customizations
                    if c.menu_item_id == menu_item.menu_item_id
                ]
                if item_customizations:
                    customization = random.choice(item_customizations)
                    db.add(
                        OrderItemCustomization(
                            order_item_id=order_item.order_item_id,
                            customization_id=customization.customization_id,
                        )
                    )

        # Calculate totals
        order_items = (
            db.query(OrderItem).filter(OrderItem.order_id == order.order_id).all()
        )
        subtotal = sum(item.price * item.quantity for item in order_items)
        tax = subtotal * Decimal("0.0825")  # 8.25% tax
        total = subtotal + tax

        order.subtotal = subtotal
        order.tax = tax
        order.total = total

        # Update table status for active orders
        table.status = "occupied"

        orders.append(order)

    db.commit()
    return orders


if __name__ == "__main__":
    seed_database()

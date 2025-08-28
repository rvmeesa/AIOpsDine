# db/seed.py
import sqlite3
from datetime import datetime, timedelta

DB_FILE = "restaurant.db"

def seed():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Insert menu items
    menu_items = [
        ("Margherita Pizza", "Classic cheese and tomato pizza", 8.5, "main", 0, 1),
        ("Vegan Burger", "Plant-based patty with lettuce and tomato", 10.0, "main", 1, 1),
        ("Caesar Salad", "Romaine, croutons, parmesan", 7.0, "starter", 0, 0),
        ("Mushroom Soup", "Creamy mushroom soup", 6.0, "starter", 0, 1),
        ("Spaghetti Carbonara", "Pasta with egg and pancetta", 11.5, "main", 0, 0),
        ("Lemonade", "Freshly squeezed lemon juice", 3.5, "drink", 1, 1),
        ("Iced Tea", "Sweetened black tea with ice", 3.0, "drink", 1, 1),
        ("Tiramisu", "Classic Italian dessert", 5.5, "dessert", 0, 0),
        ("Vegan Brownie", "Chocolate brownie made vegan", 4.5, "dessert", 1, 1),
        ("Espresso", "Strong Italian coffee", 2.5, "drink", 1, 1)
    ]
    cur.executemany("""
        INSERT INTO menu (name, description, price, category, is_vegan, is_gluten_free)
        VALUES (?, ?, ?, ?, ?, ?)
    """, menu_items)

    # Insert tables
# Insert tables
    tables = [
        (1, 2, "available"),  # table_number=1, capacity=2
        (2, 4, "available"),  # table_number=2, capacity=4
        (3, 4, "reserved"),   # table_number=3, capacity=4
        (4, 2, "occupied"),   # table_number=4, capacity=2
        (5, 6, "available"),  # table_number=5, capacity=6
        (6, 4, "available")   # table_number=6, capacity=4
    ]
    cur.executemany("""
        INSERT INTO tables (table_number, capacity, status) VALUES (?, ?, ?)
    """, tables)

    # Insert reservations
    now = datetime.now()
    reservations = [
        ("Alice Johnson", now + timedelta(hours=1), 3),
        ("Bob Smith", now + timedelta(hours=2), 2),
    ]
    cur.executemany("""
        INSERT INTO reservations (customer_name, reservation_time, table_id)
        VALUES (?, ?, ?)
    """, reservations)

    # Insert orders
    orders = [(2, 1, "served"), (4, None, "preparing")]
    cur.executemany("""
        INSERT INTO orders (table_id, reservation_id, status)
        VALUES (?, ?, ?)
    """, orders)

    # Insert order items
    order_items = [(1, 1, 2), (1, 6, 2), (2, 2, 1), (2, 5, 1)]
    cur.executemany("""
        INSERT INTO order_items (order_id, menu_id, quantity)
        VALUES (?, ?, ?)
    """, order_items)

    # Insert inventory
    inventory = [
        ("Tomatoes", 1000, "grams"),
        ("Cheese", 500, "grams"),
        ("Flour", 2000, "grams"),
        ("Lettuce", 300, "grams"),
        ("Coffee Beans", 1000, "grams"),
    ]
    cur.executemany("""
        INSERT INTO inventory (ingredient, quantity, unit)
        VALUES (?, ?, ?)
    """, inventory)

    # Insert vision events
    vision_events = [(2, "detected_occupied"), (4, "detected_empty")]
    cur.executemany("""
        INSERT INTO vision_events (table_id, event_type)
        VALUES (?, ?)
    """, vision_events)

    # Insert analytics_daily
    analytics = [
        (now.date(), 15, 200.0, 1),
        (now.date() - timedelta(days=1), 20, 300.0, 2)
    ]
    cur.executemany("""
        INSERT INTO analytics_daily (date, total_orders, total_revenue, popular_item_id)
        VALUES (?, ?, ?, ?)
    """, analytics)

    conn.commit()
    conn.close()
    print("Database seeded with sample data.")

if __name__ == "__main__":
    seed()

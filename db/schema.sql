-- MENU TABLE
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT,                -- e.g., appetizer, main, drink
    is_vegan BOOLEAN DEFAULT 0,
    is_gluten_free BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_menu_category ON menu(category);

-- TABLES (restaurant seating)
CREATE TABLE IF NOT EXISTS tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER UNIQUE NOT NULL,
    capacity INTEGER NOT NULL,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RESERVATIONS
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    reservation_time TIMESTAMP NOT NULL,
    table_id INTEGER,
    FOREIGN KEY (table_id) REFERENCES tables (id)
);

CREATE INDEX IF NOT EXISTS idx_reservations_time ON reservations(reservation_time);

-- ORDERS
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER,
    reservation_id INTEGER,
    status TEXT DEFAULT 'pending',   -- pending, preparing, served, paid
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_id) REFERENCES tables (id),
    FOREIGN KEY (reservation_id) REFERENCES reservations (id)
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- ORDER ITEMS
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (menu_id) REFERENCES menu (id)
);

-- INVENTORY
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,             -- e.g., grams, liters, pieces
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inventory_ingredient ON inventory(ingredient);

-- VISION EVENTS
CREATE TABLE IF NOT EXISTS vision_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER,
    event_type TEXT NOT NULL,       -- detected_empty, detected_occupied
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_id) REFERENCES tables (id)
);

CREATE INDEX IF NOT EXISTS idx_vision_events_time ON vision_events(timestamp);

-- ANALYTICS DAILY
CREATE TABLE IF NOT EXISTS analytics_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    total_orders INTEGER DEFAULT 0,
    total_revenue REAL DEFAULT 0.0,
    popular_item_id INTEGER,
    FOREIGN KEY (popular_item_id) REFERENCES menu (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_analytics_date ON analytics_daily(date);

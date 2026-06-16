PRAGMA foreign_keys = ON;

CREATE TABLE Product (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    spec TEXT,
    unit TEXT,
    base_price INTEGER,
    category TEXT,
    status TEXT
);

CREATE TABLE Supplier (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    avg_lead_day INTEGER
);

CREATE TABLE Warehouse (
    warehouse_id INTEGER PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    location TEXT,
    detail_location TEXT,
    manager TEXT
);

CREATE TABLE Inventory (
    inventory_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    current_qty INTEGER DEFAULT 0,
    safety_qty INTEGER DEFAULT 0,
    max_qty INTEGER,
    update_date TEXT,
    FOREIGN KEY(product_id) REFERENCES Product(product_id),
    FOREIGN KEY(warehouse_id) REFERENCES Warehouse(warehouse_id)
);

CREATE TABLE Inbound (
    inbound_id INTEGER PRIMARY KEY,
    supplier_id INTEGER,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    inbound_qty INTEGER NOT NULL,
    inbound_date TEXT,
    inspection_yn TEXT,
    manager TEXT,
    FOREIGN KEY(supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY(product_id) REFERENCES Product(product_id),
    FOREIGN KEY(warehouse_id) REFERENCES Warehouse(warehouse_id)
);

CREATE TABLE Outbound (
    outbound_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    outbound_qty INTEGER NOT NULL,
    outbound_date TEXT,
    destination TEXT,
    manager TEXT,
    FOREIGN KEY(product_id) REFERENCES Product(product_id),
    FOREIGN KEY(warehouse_id) REFERENCES Warehouse(warehouse_id)
);

CREATE TABLE SupplierProduct (
    supplier_product_id INTEGER PRIMARY KEY,
    supplier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    supply_price INTEGER,
    min_order_qty INTEGER,
    lead_day INTEGER,
    FOREIGN KEY(supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY(product_id) REFERENCES Product(product_id)
);

CREATE TABLE StockTransaction (
    transaction_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    transaction_date TEXT,
    reference_type TEXT,
    reference_id INTEGER,
    reason TEXT,
    manager TEXT,
    FOREIGN KEY(product_id) REFERENCES Product(product_id),
    FOREIGN KEY(warehouse_id) REFERENCES Warehouse(warehouse_id)
);
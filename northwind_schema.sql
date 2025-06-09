-- Northwind database schema for SQLite
-- Customers table
CREATE TABLE Customers (
    CustomerID TEXT PRIMARY KEY,
    CompanyName TEXT NOT NULL,
    ContactName TEXT,
    ContactTitle TEXT,
    Address TEXT,
    City TEXT,
    Region TEXT,
    PostalCode TEXT,
    Country TEXT,
    Phone TEXT,
    Fax TEXT
);

-- Employees table
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
    LastName TEXT NOT NULL,
    FirstName TEXT NOT NULL,
    Title TEXT,
    TitleOfCourtesy TEXT,
    BirthDate TEXT,
    HireDate TEXT,
    Address TEXT,
    City TEXT,
    Region TEXT,
    PostalCode TEXT,
    Country TEXT,
    HomePhone TEXT,
    Extension TEXT,
    Photo BLOB,
    Notes TEXT,
    ReportsTo INTEGER,
    FOREIGN KEY (ReportsTo) REFERENCES Employees(EmployeeID)
);

-- Products table
CREATE TABLE Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT NOT NULL,
    SupplierID INTEGER,
    CategoryID INTEGER,
    QuantityPerUnit TEXT,
    UnitPrice REAL,
    UnitsInStock INTEGER,
    UnitsOnOrder INTEGER,
    ReorderLevel INTEGER,
    Discontinued INTEGER
);

-- Orders table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID TEXT,
    EmployeeID INTEGER,
    OrderDate TEXT,
    RequiredDate TEXT,
    ShippedDate TEXT,
    ShipVia INTEGER,
    Freight REAL,
    ShipName TEXT,
    ShipAddress TEXT,
    ShipCity TEXT,
    ShipRegion TEXT,
    ShipPostalCode TEXT,
    ShipCountry TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Order Details table
CREATE TABLE [Order Details] (
    OrderID INTEGER,
    ProductID INTEGER,
    UnitPrice REAL,
    Quantity INTEGER,
    Discount REAL,
    PRIMARY KEY (OrderID, ProductID),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

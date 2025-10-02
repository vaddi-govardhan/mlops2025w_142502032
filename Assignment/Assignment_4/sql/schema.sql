PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Country (
  country_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Customer (
  customer_id INTEGER PRIMARY KEY,
  country_id INTEGER NOT NULL,
  FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

CREATE TABLE IF NOT EXISTS Product (
  stock_code TEXT PRIMARY KEY,
  description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Invoice (
  invoice_no TEXT PRIMARY KEY,
  invoice_date TEXT NOT NULL,
  customer_id INTEGER NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE IF NOT EXISTS InvoiceLine (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_no TEXT NOT NULL,
  stock_code TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  FOREIGN KEY (invoice_no) REFERENCES Invoice(invoice_no),
  FOREIGN KEY (stock_code) REFERENCES Product(stock_code)
);

CREATE INDEX IF NOT EXISTS idx_invoice_customer ON Invoice(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoiceline_invoice ON InvoiceLine(invoice_no);
CREATE INDEX IF NOT EXISTS idx_invoiceline_product ON InvoiceLine(stock_code);

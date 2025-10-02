import pandas as pd, sqlite3, numpy as np
from pathlib import Path

xlsx = r"C:\Users\govar\Documents\MLOPS\Assignments\Assignment_4\Online Retail.xlsx" 
df = pd.read_excel(xlsx)

# Clean
df.columns = [c.strip().replace(" ","") for c in df.columns]
df = df.dropna(subset=["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"])
df = df[(~df["InvoiceNo"].astype(str).str.startswith("C")) & (df["Quantity"]>0) & (df["UnitPrice"]>0)]
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

subset = df.head(2000).copy()  # enough to guarantee ≥1000 line items

# Build dimensions
countries = pd.DataFrame({"name": sorted(subset["Country"].unique())})
countries.insert(0, "country_id", range(1, len(countries)+1))
country_id = dict(zip(countries["name"], countries["country_id"]))

customers = subset[["CustomerID","Country"]].drop_duplicates()
customers = customers.rename(columns={"CustomerID":"customer_id","Country":"name"})
customers["country_id"] = customers["name"].map(country_id)
customers = customers.drop(columns=["name"])

products = subset[["StockCode","Description"]].drop_duplicates().rename(columns={"StockCode":"stock_code","Description":"description"})
invoices = subset[["InvoiceNo","InvoiceDate","CustomerID"]].drop_duplicates().rename(columns={"InvoiceNo":"invoice_no","InvoiceDate":"invoice_date","CustomerID":"customer_id"})
lines = subset[["InvoiceNo","StockCode","Quantity","UnitPrice"]].rename(columns={"InvoiceNo":"invoice_no","StockCode":"stock_code","Quantity":"quantity","UnitPrice":"unit_price"}).head(1500)

# Create DB + schema
db_path = Path("db/online_retail.db")
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(db_path)
conn.executescript(Path("sql/schema.sql").read_text())

# Insert
# Instead of .to_records(...)
conn.executemany(
    "INSERT OR IGNORE INTO Country(country_id,name) VALUES (?, ?)",
    countries[["country_id", "name"]].values.tolist()
)

conn.executemany(
    "INSERT OR IGNORE INTO Customer(customer_id, country_id) VALUES (?, ?)",
    customers[["customer_id", "country_id"]].values.tolist()
)

conn.executemany(
    "INSERT OR IGNORE INTO Product(stock_code, description) VALUES (?, ?)",
    products[["stock_code", "description"]].values.tolist()
)
invoices["invoice_date"] = pd.to_datetime(invoices["invoice_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
conn.executemany(
    "INSERT OR IGNORE INTO Invoice(invoice_no, invoice_date, customer_id) VALUES (?, ?, ?)",
    invoices[["invoice_no", "invoice_date", "customer_id"]].values.tolist()
)

conn.executemany(
    "INSERT INTO InvoiceLine(invoice_no, stock_code, quantity, unit_price) VALUES (?, ?, ?, ?)",
    lines[["invoice_no", "stock_code", "quantity", "unit_price"]].values.tolist()
)
conn.commit()

# Quick sanity checks
c = conn.cursor()
print("Countries:", c.execute("SELECT COUNT(*) FROM Country").fetchone()[0])
print("Customers:", c.execute("SELECT COUNT(*) FROM Customer").fetchone()[0])
print("Products:",  c.execute("SELECT COUNT(*) FROM Product").fetchone()[0])
print("Invoices:",  c.execute("SELECT COUNT(*) FROM Invoice").fetchone()[0])
print("InvoiceLine:", c.execute("SELECT COUNT(*) FROM InvoiceLine").fetchone()[0])
conn.close()
print("DB ready at", db_path)

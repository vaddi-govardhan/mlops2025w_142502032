import pandas as pd
from pymongo import MongoClient, errors
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI, maxPoolSize=50, minPoolSize=5, socketTimeoutMS=20000, serverSelectionTimeoutMS=10000, retryWrites=True)
db = client["online_retail"]
col = db["customers"]

def safe_insert_many(docs):
    if not docs: return
    try:
        col.insert_many(docs, ordered=False)
    except errors.BulkWriteError as bwe:
        print("BulkWriteError (sample):", bwe.details.get("writeErrors", [])[:2])
    except errors.PyMongoError as e:
        print("PyMongoError:", e)

df = pd.read_excel("Online Retail.xlsx")
df.columns = [c.strip().replace(" ","") for c in df.columns]
df = df.dropna(subset=["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"])
df = df[(~df["InvoiceNo"].astype(str).str.startswith("C")) & (df["Quantity"]>0) & (df["UnitPrice"]>0)]
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

docs = []
for cust_id, grp_c in df.groupby(df["CustomerID"].astype(int)):
    orders = []
    for inv_no, grp in grp_c.groupby(grp_c["InvoiceNo"].astype(str)):
        first = grp.iloc[0]
        orders.append({
            "invoiceNo": inv_no,
            "invoiceDate": first["InvoiceDate"].to_pydatetime(),
            "lines": [{"stockCode": str(r.StockCode), "quantity": int(r.Quantity), "unitPrice": float(r.UnitPrice)} for r in grp.itertuples(index=False)]
        })
    docs.append({"_id": int(cust_id), "country": str(grp_c.iloc[0]["Country"]), "orders": orders})
safe_insert_many(docs)

# Indexes
col.create_index("_id")
print("Customer-centric load complete.")

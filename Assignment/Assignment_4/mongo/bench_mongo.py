import time, json, os
from pymongo import MongoClient

URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(URI, maxPoolSize=50, minPoolSize=5)
db = client["online_retail"]
invoices = db["invoices"]
results = []

def timed(name, fn):
    t0 = time.perf_counter(); out = fn(); dt = time.perf_counter()-t0
    results.append({"task": name, "seconds": dt, "result": str(out)[:200]})

# CREATE
def c():
    invoices.update_one(
      {"_id":"INV_TEST"},
      {"$setOnInsert":{"invoiceDate":None,"customerId":999999,"country":"Testland","lines":[]}},
      upsert=True)
    invoices.update_one({"_id":"INV_TEST"}, {"$push":{"lines":{"stockCode":"TEST","quantity":2,"unitPrice":9.99}}})
timed("MONGO_CREATE", c)

# READ (top 10 customers by revenue)
def r():
    return list(invoices.aggregate([
      {"$unwind":"$lines"},
      {"$group":{"_id":"$customerId","revenue":{"$sum":{"$multiply":["$lines.quantity","$lines.unitPrice"]}}}},
      {"$sort":{"revenue":-1}}, {"$limit":10}
    ]))
timed("MONGO_READ_top10", r)

# UPDATE
def u():
    invoices.update_one({"_id":"INV_TEST"}, {"$mul":{"lines.$[].unitPrice":0.99}})
timed("MONGO_UPDATE_discount", u)

# DELETE
def d():
    invoices.delete_one({"_id":"INV_TEST"})
timed("MONGO_DELETE_test_doc", d)

print(json.dumps(results, indent=2))

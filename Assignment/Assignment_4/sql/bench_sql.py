import sqlite3, time, json

conn = sqlite3.connect("db/online_retail.db")
cur = conn.cursor()

def timed(name, fn):
    t0 = time.perf_counter(); out = fn(); dt = time.perf_counter()-t0
    return {"task": name, "seconds": dt, "result": out}

results = []

# CREATE (insert a few synthetic lines, then delete later)
def create():
    cur.execute("INSERT INTO Invoice(invoice_no, invoice_date, customer_id) VALUES ('INV_TEST','2011-12-01 00:00:00', 999999)")
    for i in range(10):
        cur.execute("INSERT INTO InvoiceLine (invoice_no,stock_code,quantity,unit_price) VALUES ('INV_TEST','TEST',1,1.0)")
    conn.commit()
results.append(timed("SQL_CREATE_10_lines", create))

# READ (top 10 customers by revenue)
def read_top10():
    cur.execute("""
      SELECT c.customer_id, SUM(il.quantity*il.unit_price) revenue
      FROM InvoiceLine il
      JOIN Invoice i ON il.invoice_no=i.invoice_no
      JOIN Customer c ON i.customer_id=c.customer_id
      GROUP BY c.customer_id ORDER BY revenue DESC LIMIT 10
    """)
    return cur.fetchall()
results.append(timed("SQL_READ_top10_customers", read_top10))

# UPDATE (1% discount on one invoice)
def update_one_invoice():
    cur.execute("UPDATE InvoiceLine SET unit_price=unit_price*0.99 WHERE invoice_no=(SELECT invoice_no FROM Invoice LIMIT 1)")
    conn.commit()
results.append(timed("SQL_UPDATE_discount", update_one_invoice))

# DELETE (remove synthetic rows)
def delete_test():
    cur.execute("DELETE FROM InvoiceLine WHERE invoice_no='INV_TEST'")
    cur.execute("DELETE FROM Invoice WHERE invoice_no='INV_TEST'")
    conn.commit()
results.append(timed("SQL_DELETE_test_rows", delete_test))

# AGG (monthly revenue)
def monthly():
    cur.execute("""
      SELECT substr(i.invoice_date,1,7) AS yyyymm, SUM(il.quantity*il.unit_price)
      FROM InvoiceLine il JOIN Invoice i ON il.invoice_no=i.invoice_no
      GROUP BY yyyymm ORDER BY yyyymm
    """)
    return cur.fetchall()
results.append(timed("SQL_AGG_monthly_revenue", monthly))

print(json.dumps(results, indent=2))

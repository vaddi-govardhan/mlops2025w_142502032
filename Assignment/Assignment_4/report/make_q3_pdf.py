import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import textwrap
from pathlib import Path

# ---------- Config ----------
sql_json_path   = Path("report/sql_results.json")
mongo_json_path = Path("report/mongo_results.json")
pdf_path        = Path("report/Q3_Performance_Comparison.pdf")

# ---------- Load JSON ----------
with open(sql_json_path) as f:
    sql_results = json.load(f)

with open(mongo_json_path) as f:
    mongo_results = json.load(f)

# ---------- Prepare data ----------
sql_tasks   = [r["task"]     for r in sql_results]
sql_times   = [r["seconds"] for r in sql_results]

mongo_tasks = [r["task"]     for r in mongo_results]
mongo_times = [r["seconds"] for r in mongo_results]

# ---------- Create charts ----------
plt.figure(figsize=(7,4))
plt.barh(sql_tasks, sql_times, color="steelblue")
plt.xlabel("Seconds")
plt.title("SQL (SQLite 2NF) – CRUD & Aggregation Timings")
plt.tight_layout()
plt.savefig("report/sql_chart.png", dpi=160)
plt.close()

plt.figure(figsize=(7,4))
plt.barh(mongo_tasks, mongo_times, color="seagreen")
plt.xlabel("Seconds")
plt.title("MongoDB (Document-oriented) – CRUD & Aggregation Timings")
plt.tight_layout()
plt.savefig("report/mongo_chart.png", dpi=160)
plt.close()

# ---------- Make PDF ----------
with PdfPages(pdf_path) as pdf:
    fig = plt.figure(figsize=(8.27, 11.69))  # A4
    ax = fig.add_axes([0,0,1,1])
    ax.axis("off")

    title = "Q3: CRUD Performance – SQL vs MongoDB"
    para = """
    This report compares basic CRUD + aggregation timings between:
      1) SQL – 2nd-normal-form SQLite schema
      2) MongoDB – transaction-centric document model

    The timings were collected on the same subset of the UCI Online Retail dataset.
    Measurements are approximate and for educational comparison only.
    """

    observations = """
    • SQL performed well on aggregation and reads due to indexed joins.
    • MongoDB's insertMany is usually very fast for bulk inserts.
    • Updates in the document model may touch a larger document but avoid joins.
    • Transaction-centric doc model favors per-invoice operations,
      while customer-centric favors cross-order lookups.
    • For large datasets with good indexes, MongoDB aggregation pipelines
      often scale well for read-heavy workloads.
    """

    # Title + description
    ax.text(0.5, 0.96, title, ha="center", va="top",
            fontsize=16, fontweight="bold")

    ax.text(0.05, 0.90,
            "\n".join(textwrap.fill(para.strip(), 100).splitlines()),
            ha="left", va="top", fontsize=10)

    # Add SQL chart image
    img_sql = plt.imread("report/sql_chart.png")
    ax.imshow(img_sql, extent=[0.05, 0.95, 0.48, 0.82], aspect='auto')

    # SQL timing table
    sql_text = "SQL Timings:\n" + "\n".join(
        f"  • {t}: {s:.4f}s" for t,s in zip(sql_tasks, sql_times))
    ax.text(0.05, 0.45, sql_text, ha="left", va="top", fontsize=10)

    # Add Mongo chart image
    img_mongo = plt.imread("report/mongo_chart.png")
    ax.imshow(img_mongo, extent=[0.05, 0.95, 0.10, 0.42], aspect='auto')

    # Observations
    ax.text(0.05, 0.07,
            "\n".join(textwrap.fill(observations.strip(), 100).splitlines()),
            ha="left", va="bottom", fontsize=10)

    pdf.savefig(fig)
    plt.close(fig)

print(f"PDF saved at: {pdf_path.resolve()}")

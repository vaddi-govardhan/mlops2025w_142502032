"""
mongo_students_demo.py

Requirements:
    pip install pymongo

Usage:
    - Set MONGO_URI to your MongoDB connection string (default is localhost).
    - Run: python mongo_students_demo.py

What it does:
    - Creates 'student_db' and 'students' collection
    - Inserts 100 synthetic student docs
    - Demonstrates CRUD (create/read/update/delete)
    - Runs analytics queries using aggregation pipelines
"""

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import random

# ---------- CONFIG ----------
MONGO_URI = "mongodb://localhost:27017"   
DB_NAME = "student_db"
COLLECTION_NAME = "students"
NUM_RECORDS = 100
random.seed(42)
# ----------------------------

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
students = db[COLLECTION_NAME]

def reset_collection():
    """Drop collection if exists to run demo cleanly."""
    if COLLECTION_NAME in db.list_collection_names():
        db.drop_collection(COLLECTION_NAME)
    print("Collection reset.")

def generate_synthetic_students(n=100):
    first_names = ["Aarav","Nikhil","Isha","Priya","Rahul","Sana","Rohit","Neha","Vijay","Ananya",
                   "Karan","Mira","Akash","Ritika","Manish","Divya","Siddharth","Pooja","Arjun","Tanya"]
    last_names = ["Sharma","Reddy","Kumar","Gupta","Singh","Patel","Nair","Das","Iyer","Verma"]
    courses = ["B.Tech", "BSc", "BCA", "BBA", "BCom"]
    majors = ["Computer Science", "Electronics", "Mechanical", "Mathematics", "Economics"]
    minors = ["Data Science", "AI", "Cybersecurity", "Business Analytics", None]  # None => no minor
    years = [1, 2, 3, 4]

    docs = []
    for i in range(1, n+1):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(17, 24)
        year = random.choice(years)
        regno = f"REG{datetime.now().year}{i:04d}"   # e.g., REG20250001
        course = random.choice(courses)
        major = random.choice(majors)
        minor = random.choice(minors)
        # To make distribution realistic: more seniors in higher year
        created_at = datetime.utcnow()
        doc = {
            "name": name,
            "age": age,
            "year": year,
            "regno": regno,
            "course": course,
            "major": major,
            "minor": minor,
            "created_at": created_at
        }
        docs.append(doc)
    return docs

# ---------------------------
# CRUD Demonstration
# ---------------------------

def create_indexes():
    # unique index on regno to avoid duplicates
    students.create_index([("regno", ASCENDING)], unique=True)
    # Indexes to speed queries
    students.create_index([("major", ASCENDING)])
    students.create_index([("year", ASCENDING)])
    print("Indexes created: regno(unique), major, year")

def insert_students(docs):
    try:
        result = students.insert_many(docs, ordered=False)
        print(f"Inserted {len(result.inserted_ids)} students")
    except DuplicateKeyError as e:
        print("Duplicate key error while inserting (some regno duplicates?).", e)
    except Exception as e:
        print("Insert error:", e)

def create_one_student():
    new_student = {
        "name": "Test Student",
        "age": 20,
        "year": 2,
        "regno": f"REG{datetime.now().year}9999",
        "course": "B.Tech",
        "major": "Computer Science",
        "minor": "Data Science",
        "created_at": datetime.utcnow()
    }
    res = students.insert_one(new_student)
    print("Created one student with _id:", res.inserted_id)
    return new_student

def read_examples():
    print("\n--- Read examples ---")
    # Find one
    one = students.find_one({})
    print("One document (sample):", one)

    # Find by filter: all 3rd year students
    third_year = list(students.find({"year": 3}).limit(5))
    print(f"Sample 3rd-year students (up to 5): {len(third_year)} found")
    for s in third_year:
        print("  ", s["regno"], s["name"], s["major"])

    # Find students with minor != None
    minors = students.count_documents({"minor": {"$ne": None}})
    total = students.count_documents({})
    print(f"Students with minors: {minors} / {total}")

def update_examples():
    print("\n--- Update examples ---")
    # Update one student's major
    target = students.find_one({"regno": {"$regex": "9999$"}})  # the Test Student created earlier
    if target:
        students.update_one({"_id": target["_id"]}, {"$set": {"major": "Artificial Intelligence"}})
        print("Updated Test Student major to Artificial Intelligence")

    # Promote all 3rd year students to 4th year (example of update_many)
    res = students.update_many({"year": 3}, {"$set": {"year": 4}})
    print(f"Promoted {res.modified_count} students from year 3 to year 4")

def delete_examples():
    print("\n--- Delete examples ---")
    # Delete the test student
    res = students.delete_many({"regno": {"$regex": "9999$"}})
    print(f"Deleted {res.deleted_count} test students (regno ending 9999)")

    # Example: remove students with age < 18 (if any)
    res2 = students.delete_many({"age": {"$lt": 18}})
    print(f"Deleted {res2.deleted_count} students with age < 18 (example)")

# ---------------------------
# Analytics (Aggregation)
# ---------------------------

def analytics_examples():
    print("\n--- Analytics ---")

    # 1) Count students by year
    pipeline_year_count = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    year_counts = list(students.aggregate(pipeline_year_count))
    print("Students per year:", year_counts)

    # 2) Average age per major
    pipeline_avg_age_major = [
        {"$group": {"_id": "$major", "avg_age": {"$avg": "$age"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    avg_age_major = list(students.aggregate(pipeline_avg_age_major))
    print("Average age per major (major, avg_age, count):")
    for doc in avg_age_major:
        print("  ", doc)

    # 3) Top 3 majors by number of students
    pipeline_top_majors = [
        {"$group": {"_id": "$major", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 3}
    ]
    top_majors = list(students.aggregate(pipeline_top_majors))
    print("Top 3 majors:", top_majors)

    # 4) Course distribution
    pipeline_course_dist = [
        {"$group": {"_id": "$course", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    course_dist = list(students.aggregate(pipeline_course_dist))
    print("Course distribution:", course_dist)

    # 5) Percentage of students with a minor
    total = students.count_documents({})
    with_minor = students.count_documents({"minor": {"$ne": None}})
    percent_minor = (with_minor / total * 100) if total else 0
    print(f"Percent with minor: {percent_minor:.1f}% ({with_minor}/{total})")

    # 6) Students per course-major combination (heatmap-ready)
    pipeline_course_major = [
        {"$group": {"_id": {"course": "$course", "major": "$major"}, "count": {"$sum": 1}}},
        {"$project": {"course": "$_id.course", "major": "$_id.major", "count": 1, "_id": 0}},
        {"$sort": {"count": -1}}
    ]
    cm = list(students.aggregate(pipeline_course_major))
    print("Students per (course, major) combination - top 10:")
    for doc in cm[:10]:
        print("  ", doc)

    # 7) Example combined filter & aggregation: avg age of seniors (year 4) with minors
    pipeline_seniors_minors = [
        {"$match": {"year": 4, "minor": {"$ne": None}}},
        {"$group": {"_id": None, "avg_age": {"$avg": "$age"}, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "avg_age": 1, "count": 1}}
    ]
    seniors_minors = list(students.aggregate(pipeline_seniors_minors))
    print("Senior (year 4) students with minors ->", seniors_minors)

    # 8) Example: find students with same major and minor (possible double-specialization)
    pipeline_same_major_minor = [
        {"$match": {"minor": {"$ne": None}}},
        {"$project": {"name": 1, "major": 1, "minor": 1}},
        {"$match": {"$expr": {"$eq": ["$major", "$minor"]}}}
    ]
    same_mm = list(students.aggregate(pipeline_same_major_minor))
    print("Students with same major and minor (rare):", same_mm)

# ---------------------------
# Putting it all together
# ---------------------------

def main():
    reset_collection()
    create_indexes()  # will create even for empty collection
    docs = generate_synthetic_students(NUM_RECORDS)
    insert_students(docs)

    # Additional operations
    sample_new = create_one_student()
    read_examples()
    update_examples()
    analytics_examples()
    delete_examples()

    # Final counts
    final_total = students.count_documents({})
    print(f"\nFinal total documents in '{DB_NAME}.{COLLECTION_NAME}': {final_total}")

    # Print a small sample to visually inspect
    print("\nSample 5 documents:")
    for doc in students.find({}, {"_id": 0}).limit(5):
        print(" ", doc)

if __name__ == "__main__":
    main()

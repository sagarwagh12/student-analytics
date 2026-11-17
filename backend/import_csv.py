import csv
from pathlib import Path
from datetime import datetime, timezone
from main import connect, init_db, BASE

def run():
    init_db()
    students_file = BASE / "data" / "sample_students.csv"
    records_file = BASE / "data" / "sample_records.csv"
    with connect() as con:
        with students_file.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                con.execute("""INSERT OR REPLACE INTO students
                    (student_id,name,class_name,section,email) VALUES (?,?,?,?,?)""",
                    (row["student_id"], row["name"], row["class_name"], row["section"], row["email"]))
        with records_file.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                con.execute("""INSERT INTO records
                    (student_id,subject,exam,marks,attendance,record_date,created_at)
                    VALUES (?,?,?,?,?,?,?)""",
                    (row["student_id"], row["subject"], row["exam"], float(row["marks"]),
                     float(row["attendance"]), row["record_date"], datetime.now(timezone.utc).isoformat()))
    print("CSV import complete.")

if __name__ == "__main__":
    run()

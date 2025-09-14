from pathlib import Path
import csv
import datetime

from university.models import FieldOfStudy
from university.repositories import InMemoryRepository
from university.services import UniversityService
from university.validators import (
    parse_field_of_study, validate_age, validate_year, validate_grade
)

# ---------- Small input helpers with retry ----------

def require_nonempty(s: str) -> str:
    if not s.strip():
        raise ValueError("Value is required.")
    return s.strip()

def ask(prompt, caster=str, validator=None):
    """Ask until valid. caster converts the string; validator may raise ValueError."""
    while True:
        s = input(prompt)
        try:
            val = caster(s)
            if validator:
                validator(val)
            return val
        except Exception as e:
            print(f"⚠️  {e} — try again.")

def show_field_menu() -> None:
    print("Choose field:")
    for i, f in enumerate(FieldOfStudy, start=1):
        print(f"  {i}) {f.name.title().replace('_',' ')}")
    print("  (You can type the number or a name/alias like 'CS' or 'Software')")

def ask_single_field(prompt="Field: ") -> FieldOfStudy:
    while True:
        show_field_menu()
        s = input(prompt)
        try:
            return parse_field_of_study(s)
        except Exception as e:
            print(f"⚠️  {e} — please choose again.")

def ask_multi_fields(prompt="Fields (comma-separated or numbers): "):
    while True:
        show_field_menu()
        raw = input(prompt).strip()
        try:
            tokens = [t.strip() for t in raw.replace("/", ",").split(",") if t.strip()]
            if not tokens:
                raise ValueError("At least one field is required.")
            fields = [parse_field_of_study(t) for t in tokens]
            return fields
        except Exception as e:
            print(f"⚠️  {e} — please try again.")

# ---------- Export helper ----------

def export_personnel_csv(service: UniversityService, filename: str = "personnel.csv") -> Path:
    """
    Exports all students and teachers to a CSV file next to this app.py.
    Returns the full path to the created file.
    """
    root = Path(__file__).parent
    path = root / filename

    students = service.list_students()
    teachers = service.list_teachers()

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["exported_at", datetime.datetime.now().isoformat(timespec="seconds")])
        w.writerow([])  # blank line
        w.writerow(["type", "id", "name", "age", "major_or_fields", "year_or_seniority", "grade_1_100"])

        # Students
        for s in students:
            w.writerow([
                "student",
                s.id,
                s.name,
                s.age,
                s.major.name.title().replace("_", " "),
                s.year,
                s.average_grade,
            ])

        # Teachers
        for t in teachers:
            fields_str = "; ".join(f.name.title().replace("_", " ") for f in t.fields)
            w.writerow([
                "teacher",
                t.id,
                t.name,
                t.age,
                fields_str,
                t.seniority_years,
                "",  # no grade for teachers
            ])

    return path

# ---------- CLI ----------

def print_menu():
    print("\n==== University System ====")
    print("1) Add Student")
    print("2) Add Teacher")
    print("3) List Students")
    print("4) List Teachers")
    print("5) Export all personnel to CSV")  # NEW
    print("0) Exit")

def main():
    service = UniversityService(
        student_repo=InMemoryRepository(),
        teacher_repo=InMemoryRepository(),
    )

    while True:
        print_menu()
        choice = input("> ").strip()

        if choice == "1":
            name = ask("Name: ", caster=require_nonempty)
            age = ask("Age: ", caster=int, validator=validate_age)
            major = ask_single_field("Major: ")
            year = ask("Year (1-8): ", caster=int, validator=validate_year)
            average_grade = ask("Overall grade (1-100): ", caster=int, validator=validate_grade)
            try:
                s = service.add_student(name, age, major, year, average_grade)
                print("✅ Added:", s.summary())
            except Exception as e:
                print(f"❌ Could not add student: {e}")

        elif choice == "2":
            name = ask("Name: ", caster=require_nonempty)
            age = ask("Age: ", caster=int, validator=validate_age)
            seniority = ask(
                "Seniority (years): ",
                caster=int,
                validator=lambda x: 0 <= x <= 80 or (_ for _ in ()).throw(ValueError("Seniority years must be between 0 and 80."))
            )
            fields = ask_multi_fields("Fields: ")
            try:
                t = service.add_teacher(name, age, seniority, fields)
                print("✅ Added:", t.summary())
            except Exception as e:
                print(f"❌ Could not add teacher: {e}")

        elif choice == "3":
            students = service.list_students()
            if not students:
                print("No students yet.")
            for s in students:
                print(s.summary())

        elif choice == "4":
            teachers = service.list_teachers()
            if not teachers:
                print("No teachers yet.")
            for t in teachers:
                print(t.summary())

        elif choice == "5":
            try:
                path = export_personnel_csv(service)
                print(f"✅ Exported to: {path}")
            except Exception as e:
                print(f"❌ Export failed: {e}")

        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Unknown option.")

if __name__ == "__main__":
    main()

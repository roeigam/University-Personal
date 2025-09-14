from typing import List
from .models import Student, Teacher, FieldOfStudy
from .repositories import Repository
from .validators import validate_age, validate_year, validate_grade

class UniversityService:
    def __init__(self, student_repo: Repository[Student], teacher_repo: Repository[Teacher]):
        self.students = student_repo
        self.teachers = teacher_repo

    # ---- Students ----
    def add_student(self, name: str, age: int, major: FieldOfStudy, year: int, average_grade: int) -> Student:
        validate_age(age)
        validate_year(year)
        validate_grade(average_grade)
        s = Student(name=name, age=age, major=major, year=year, average_grade=average_grade)
        return self.students.add(s)

    def list_students(self) -> List[Student]:
        return self.students.list_all()

    # ---- Teachers ----
    def add_teacher(self, name: str, age: int, seniority_years: int, fields: List[FieldOfStudy]) -> Teacher:
        validate_age(age)
        if seniority_years < 0 or seniority_years > 80:
            raise ValueError("Seniority years must be between 0 and 80.")
        if not fields:
            raise ValueError("Teacher must have at least one field.")
        t = Teacher(name=name, age=age, seniority_years=seniority_years, fields=fields)
        return self.teachers.add(t)

    def list_teachers(self) -> List[Teacher]:
        return self.teachers.list_all()

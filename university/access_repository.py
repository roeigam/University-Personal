from __future__ import annotations
from pathlib import Path
from typing import List
import pyodbc

from .models import Student, Teacher, FieldOfStudy

DRIVER = "{Microsoft Access Driver (*.mdb, *.accdb)}"

def _connect(db_path: Path) -> pyodbc.Connection:
    conn_str = f"DRIVER={DRIVER};DBQ={db_path};"
    # autocommit simplifies DDL and identity retrieval
    return pyodbc.connect(conn_str, autocommit=True)

def _ensure_schema(conn: pyodbc.Connection) -> None:
    cur = conn.cursor()
    # Students table
    try:
        cur.execute("""
            CREATE TABLE Students (
                id AUTOINCREMENT PRIMARY KEY,
                name TEXT(255),
                age INTEGER,
                major TEXT(64),
                [year] INTEGER,
                average_grade INTEGER
            )
        """)
    except Exception:
        pass  # already exists
    # Teachers table
    try:
        cur.execute("""
            CREATE TABLE Teachers (
                id AUTOINCREMENT PRIMARY KEY,
                name TEXT(255),
                age INTEGER,
                seniority_years INTEGER,
                fields TEXT(255)
            )
        """)
    except Exception:
        pass
    cur.close()

class AccessStudentRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = _connect(self.db_path)
        _ensure_schema(self.conn)

    def add(self, s: Student) -> Student:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Students (name, age, major, [year], average_grade) VALUES (?, ?, ?, ?, ?)",
            s.name, s.age, s.major.name, s.year, s.average_grade
        )
        new_id = cur.execute("SELECT @@IDENTITY").fetchone()[0]
        s.id = int(new_id)  # overwrite dataclass auto-id with DB id
        cur.close()
        return s

    def list_all(self) -> List[Student]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT id, name, age, major, [year], average_grade FROM Students ORDER BY id"
        ).fetchall()
        out: List[Student] = []
        for r in rows:
            major = FieldOfStudy[r[3]]  # stored by enum .name
            stu = Student(name=r[1], age=int(r[2]), major=major, year=int(r[4]), average_grade=int(r[5]))
            stu.id = int(r[0])
            out.append(stu)
        cur.close()
        return out

    def find(self, predicate):
        return [s for s in self.list_all() if predicate(s)]

class AccessTeacherRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = _connect(self.db_path)
        _ensure_schema(self.conn)

    def add(self, t: Teacher) -> Teacher:
        fields_str = ";".join(f.name for f in t.fields)  # store enum names joined
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO Teachers (name, age, seniority_years, fields) VALUES (?, ?, ?, ?)",
            t.name, t.age, t.seniority_years, fields_str
        )
        new_id = cur.execute("SELECT @@IDENTITY").fetchone()[0]
        t.id = int(new_id)
        cur.close()
        return t

    def list_all(self) -> List[Teacher]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT id, name, age, seniority_years, fields FROM Teachers ORDER BY id"
        ).fetchall()
        out: List[Teacher] = []
        for r in rows:
            fields = [FieldOfStudy[name] for name in (r[4] or "").split(";") if name]
            tch = Teacher(name=r[1], age=int(r[2]), seniority_years=int(r[3]), fields=fields)
            tch.id = int(r[0])
            out.append(tch)
        cur.close()
        return out

    def find(self, predicate):
        return [t for t in self.list_all() if predicate(t)]

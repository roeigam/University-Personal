# university/models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod
from enum import Enum, auto
import itertools


class FieldOfStudy(Enum):
    COMPUTER_SCIENCE = auto()
    ELECTRICAL_ENGINEERING = auto()
    MECHANICAL_ENGINEERING = auto()
    MATHEMATICS = auto()
    PHYSICS = auto()
    LITERATURE = auto()
    HISTORY = auto()


_id_counter = itertools.count(1)  # simple ID generator


@dataclass
class Person(ABC):
    """Abstract base for people at the university."""
    name: str
    age: int
    id: int = field(default_factory=lambda: next(_id_counter), init=False)

    @abstractmethod
    def summary(self) -> str:
        ...


@dataclass
class Student(Person):
    major: FieldOfStudy
    year: int
    average_grade: int  # 1..100

    def summary(self) -> str:
        return (f"[Student] #{self.id} {self.name} (age {self.age}) | "
                f"Major: {self.major.name.title().replace('_',' ')} | "
                f"Year: {self.year} | Grade: {self.average_grade}/100")


@dataclass
class Teacher(Person):
    seniority_years: int
    fields: List[FieldOfStudy]

    def summary(self) -> str:
        flds = ", ".join(f.name.replace('_',' ').title() for f in self.fields) or "N/A"
        return (f"[Teacher] #{self.id} {self.name} (age {self.age}) | "
                f"Seniority: {self.seniority_years} yrs | Fields: {flds}")

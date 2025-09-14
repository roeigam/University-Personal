from .models import FieldOfStudy

def validate_age(age: int) -> None:
    if age < 15 or age > 100:
        raise ValueError("Age must be between 15 and 100.")

def validate_year(year: int) -> None:
    if year < 1 or year > 8:
        raise ValueError("Year must be between 1 and 8.")

def validate_grade(grade: int) -> None:
    if grade < 1 or grade > 100:
        raise ValueError("Overall grade must be between 1 and 100.")

# Friendly aliases for typing majors quickly
ALIASES = {
    "CS": "COMPUTER_SCIENCE",
    "COMP_SCI": "COMPUTER_SCIENCE",
    "SOFTWARE": "COMPUTER_SCIENCE",  # change if you added SOFTWARE_ENGINEERING enum
    "SWE": "COMPUTER_SCIENCE",
    "SE": "COMPUTER_SCIENCE",
    "SW": "COMPUTER_SCIENCE",
    "EE": "ELECTRICAL_ENGINEERING",
    "ME": "MECHANICAL_ENGINEERING",
}

def parse_field_of_study(raw: str) -> FieldOfStudy:
    s = raw.strip()
    # also accept a number from the on-screen menu
    if s.isdigit():
        idx = int(s)
        items = list(FieldOfStudy)
        if 1 <= idx <= len(items):
            return items[idx - 1]
    normalized = s.replace(" ", "_").upper()
    normalized = ALIASES.get(normalized, normalized)
    try:
        return FieldOfStudy[normalized]
    except KeyError:
        available = ", ".join(f.name.title().replace("_"," ") for f in FieldOfStudy)
        raise ValueError(f"Unknown field of study: {raw}. Available: {available}")

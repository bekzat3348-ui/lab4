import sys
import unittest
from types import ModuleType

# 1. MODULE: university_rating.validation
validation = ModuleType("university_rating.validation")


def validate_scores(scores):
    if not isinstance(scores, (list, tuple)):
        raise TypeError("scores must be a list or tuple")
    checked = []
    for score in scores:
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("Score must be a number")
        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100")
        checked.append(float(score))
    return checked


def validate_student(student):
    if not isinstance(student, dict):
        raise TypeError("Student entry must be a dictionary")
    required = {"id", "name", "scores"}
    missing = required - student.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")


validation.validate_scores = validate_scores
validation.validate_student = validate_student
sys.modules["university_rating.validation"] = validation


# 2. MODULE: university_rating.calculations
calculations = ModuleType("university_rating.calculations")

PASSING_AVERAGE = 50


def calculate_average(scores):
    return sum(scores) / len(scores) if scores else None


def determine_status(average):
    if average is None:
        return "no data"
    return "passed" if average >= PASSING_AVERAGE else "failed"


def get_letter_grade(average):
    if average is None:
        return "N/A"
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


calculations.PASSING_AVERAGE = PASSING_AVERAGE
calculations.calculate_average = calculate_average
calculations.determine_status = determine_status
calculations.get_letter_grade = get_letter_grade
sys.modules["university_rating.calculations"] = calculations


# 3. MODULE: university_rating.rating
rating = ModuleType("university_rating.rating")


def build_student_result(student):
    validate_student(student)
    scores = validate_scores(student["scores"])
    average = calculate_average(scores)
    return {
        "id": student["id"],
        "name": student["name"],
        "average": average,
        "status": determine_status(average),
        "grade": get_letter_grade(average),
    }


def _sort_key(item):
    average = item["average"]
    return average is not None, average or 0


def build_rating(students):
    results = [build_student_result(item) for item in students]
    return sorted(results, key=_sort_key, reverse=True)


rating.build_student_result = build_student_result
rating._sort_key = _sort_key
rating.build_rating = build_rating
sys.modules["university_rating.rating"] = rating


# 4. MODULE: university_rating.report
report = ModuleType("university_rating.report")


def format_average(value):
    return "—" if value is None else f"{value:.2f}"


def format_rating(rows):
    lines = ["Group Rating"]
    for position, row in enumerate(rows, start=1):
        average = format_average(row["average"])
        lines.append(
            f"{position}. {row['name']}: {average} (Grade: {row['grade']}) — {row['status']}"
        )
    return "\n".join(lines)


report.format_average = format_average
report.format_rating = format_rating
sys.modules["university_rating.report"] = report


# 5. MODULE: university_rating (__init__)
pkg = ModuleType("university_rating")
pkg.build_rating = build_rating
pkg.build_student_result = build_student_result
pkg.__all__ = ["build_rating", "build_student_result"]
sys.modules["university_rating"] = pkg


# 6. DEMO / MAIN ENTRY POINT
def load_demo_data():
    return [
        {"id": 101, "name": "Amina", "scores": [88, 92, 79]},
        {"id": 102, "name": "Dias", "scores": [45, 52, 48]},
        {"id": 103, "name": "Mira", "scores": []},
    ]


def run_app():
    print("=== PROGRAM OUTPUT ===")
    students = load_demo_data()
    rating_data = build_rating(students)
    print(format_rating(rating_data))
    print("\n" + "=" * 22 + "\n")


# 7. AUTOMATED TESTS
class RatingTests(unittest.TestCase):
    def test_empty_average(self):
        self.assertIsNone(calculate_average([]))

    def test_status_boundary(self):
        self.assertEqual(determine_status(49.99), "failed")
        self.assertEqual(determine_status(50), "passed")

    def test_invalid_score(self):
        with self.assertRaises(ValueError):
            validate_scores([80, 101])

    def test_source_is_not_changed(self):
        students = [{"id": 1, "name": "Test", "scores": [70, 80]}]
        before = [{"id": 1, "name": "Test", "scores": [70, 80]}]
        build_rating(students)
        self.assertEqual(students, before)

    def test_letter_grade_calculation(self):
        self.assertEqual(get_letter_grade(95), "A")
        self.assertEqual(get_letter_grade(85), "B")
        self.assertEqual(get_letter_grade(75), "C")
        self.assertEqual(get_letter_grade(65), "D")
        self.assertEqual(get_letter_grade(40), "F")

    def test_letter_grade_none(self):
        self.assertEqual(get_letter_grade(None), "N/A")


if __name__ == "__main__":
    run_app()

    print("=== UNITTEST RESULTS ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(RatingTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

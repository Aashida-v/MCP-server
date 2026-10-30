import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server import calculate_grade, create_study_plan, search_study_notes

# -------------------- calculate_grade --------------------

def test_calculate_grade_valid():
    result = calculate_grade(85, 100)
    assert result["percentage"] == 85.0
    assert result["grade"] == "B"

def test_calculate_grade_invalid_total():
    result = calculate_grade(50, 0)
    assert "error" in result
    assert "positive" in result["error"].lower()

def test_calculate_grade_invalid_marks():
    result = calculate_grade(110, 100)
    assert "error" in result
    assert "between 0" in result["error"].lower()

# -------------------- create_study_plan --------------------

def test_create_study_plan_valid():
    subjects = ["Math", "Physics"]
    hours_per_day = 4
    days = 2
    result = create_study_plan(subjects, hours_per_day, days)
    schedule = result.get("schedule")
    assert schedule is not None
    assert len(schedule) == days
    for day in range(1, days + 1):
        allocations = schedule[day]
        assert len(allocations) == len(subjects)
        for alloc in allocations:
            assert "subject" in alloc and "hours" in alloc
    total_allocated = sum(alloc["hours"] for day_alloc in schedule.values() for alloc in day_alloc)
    assert total_allocated == pytest.approx(hours_per_day * days, rel=1e-2)

def test_create_study_plan_empty_subjects():
    result = create_study_plan([], 3, 1)
    assert "error" in result

def test_create_study_plan_negative_hours():
    result = create_study_plan(["History"], -1, 1)
    assert "error" in result

# -------------------- search_study_notes --------------------

def test_search_study_notes_match():
    result = search_study_notes("learning")
    matches = result.get("matches")
    assert isinstance(matches, list)
    assert any(m["file"] == "machine_learning.txt" for m in matches)

def test_search_study_notes_no_match():
    result = search_study_notes("nonexistentterm")
    assert result.get("matches") == []

def test_search_study_notes_empty_query():
    result = search_study_notes("")
    assert result.get("matches") == []

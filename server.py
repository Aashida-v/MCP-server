import sys
import json
from pathlib import Path
from typing import List, Dict, Any

from fastmcp import FastMCP

# Initialize FastMCP server with a name
mcp = FastMCP("Student Productivity MCP Server")

# Helper function to output errors in a standard way (used by tools)
def _error(message: str) -> Dict[str, Any]:
    return {"error": message}

@mcp.tool(description="Calculate grade percentage and classification based on obtained and total marks.")
def calculate_grade(marks_obtained: float, total_marks: float) -> Dict[str, Any]:
    """Validate inputs and return percentage and letter grade.

    Returns a dictionary with keys:
        - percentage: float (0‑100)
        - grade: str (A, B, C, D, F)
    If validation fails, returns a dict with an "error" key.
    """
    if total_marks <= 0:
        return _error("total_marks must be a positive number.")
    if marks_obtained < 0 or marks_obtained > total_marks:
        return _error("marks_obtained must be between 0 and total_marks.")
    percentage = (marks_obtained / total_marks) * 100
    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"
    return {"percentage": round(percentage, 2), "grade": grade}

@mcp.tool(description="Create a deterministic study plan schedule.")
def create_study_plan(subjects: List[str], hours_per_day: float, days: int) -> Dict[str, Any]:
    """Return a simple deterministic schedule.

    The result is a dict with a "schedule" key, mapping each day (1‑based) to a list of
    subject allocations. Hours are evenly split across subjects and days.
    """
    if not subjects:
        return _error("subjects list cannot be empty.")
    if hours_per_day <= 0:
        return _error("hours_per_day must be positive.")
    if days <= 0:
        return _error("days must be a positive integer.")

    total_hours = hours_per_day * days
    per_subject_total = total_hours / len(subjects)
    # Distribute per_subject_total across days evenly
    per_day_per_subject = per_subject_total / days
    per_day_per_subject = round(per_day_per_subject, 2)

    schedule: Dict[int, List[Dict[str, Any]]] = {}
    for day in range(1, days + 1):
        allocations = []
        for subj in subjects:
            allocations.append({"subject": subj, "hours": per_day_per_subject})
        schedule[day] = allocations
    return {"schedule": schedule}

@mcp.tool(description="Search study notes for a query string.")
def search_study_notes(query: str) -> Dict[str, Any]:
    """Search all .txt files inside the project's notes folder.

    Returns a list of matches, each containing the filename and the matching line.
    If the query is empty, returns an empty list.
    """
    if not query:
        return {"matches": []}
    notes_dir = Path(__file__).parent / "notes"
    if not notes_dir.is_dir():
        return {"matches": []}
    matches: List[Dict[str, str]] = []
    lower_query = query.lower()
    for txt_file in notes_dir.rglob("*.txt"):
        try:
            for line_no, line in enumerate(txt_file.read_text(encoding="utf-8").splitlines(), start=1):
                if lower_query in line.lower():
                    matches.append({
                        "file": txt_file.name,
                        "line": line.strip(),
                        "line_number": line_no,
                    })
        except Exception:
            # Silently skip unreadable files
            continue
    return {"matches": matches}

if __name__ == "__main__":
    # Run the MCP server over stdio (default for FastMCP)
    mcp.run()

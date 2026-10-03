"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 1
Topic: Campus Merit Analyzer using Compound Data Structures
CO Mapping: CO-2, CO-4
Bloom Level: L4 (Analyze)

Description:
    Processes student academic records stored across lists, tuples, and dictionaries.
    1. Groups students by semester and outputs Top-K students sorted by:
       - CPI (Descending)
       - Average Marks (Descending)
       - Enrollment Number (Ascending / Lexicographical)
    2. Identifies subject-wise toppers for subject codes S1 to Sm.
"""

from collections import defaultdict
import sys


def parse_student_record(line: str, num_subjects: int) -> dict:
    """
    Parses a single input line into a structured student record.
    
    Args:
        line: Space-separated line containing enrollment, name, sem, cpi, marks...
        num_subjects: Total number of subjects (m)
        
    Returns:
        dict: Processed record with enrollment, name, semester, cpi, marks tuple, and avg_marks.
    """
    tokens = line.strip().split()
    if len(tokens) != 4 + num_subjects:
        raise ValueError("Invalid number of arguments in input line.")
        
    enrollment = tokens[0]
    name = tokens[1]
    semester = int(tokens[2])
    cpi = float(tokens[3])
    
    # Store marks as an immutable tuple (Compound Data Structure)
    marks = tuple(int(x) for x in tokens[4:])
    
    # Calculate average marks for tie-breaking
    avg_marks = sum(marks) / len(marks) if marks else 0.0
    
    return {
        "enrollment": enrollment,
        "name": name,
        "semester": semester,
        "cpi": cpi,
        "marks": marks,
        "avg_marks": avg_marks
    }


def process_campus_merit(n: int, k: int, m: int, raw_records: list[str]) -> tuple[dict, dict]:
    """
    Groups, sorts, and extracts semester top-K students and subject toppers.
    
    Returns:
        sem_top_k: Dict mapping semester -> list of top-K student enrollment IDs
        subject_toppers: Dict mapping subject_code -> list of topper enrollment IDs
    """
    semesters = defaultdict(list)
    # Map subject index (0..m-1) -> list of (marks, enrollment)
    subject_marks = defaultdict(list)
    
    for line in raw_records:
        if not line.strip():
            continue
        student = parse_student_record(line, m)
        
        # Group by semester
        semesters[student["semester"]].append(student)
        
        # Group by subject
        for idx, mark in enumerate(student["marks"]):
            subject_marks[idx].append((mark, student["enrollment"]))

    # 1. Process Semester-wise Top-K
    sem_top_k = {}
    for sem in sorted(semesters.keys()):
        students = semesters[sem]
        
        # Multi-attribute sorting using tuple key:
        # (-cpi, -avg_marks, enrollment)
        # Note: CPI & avg_marks are negated for descending order; enrollment is natural for ascending.
        students.sort(key=lambda s: (-s["cpi"], -s["avg_marks"], s["enrollment"]))
        
        # Extract top K enrollments
        sem_top_k[sem] = [s["enrollment"] for s in students[:k]]

    # 2. Process Subject-wise Toppers
    subject_toppers = {}
    for idx in range(m):
        subject_code = f"S{idx + 1}"
        entries = subject_marks[idx]
        
        if not entries:
            subject_toppers[subject_code] = []
            continue
            
        # Find maximum mark in this subject
        max_mark = max(entries, key=lambda x: x[0])[0]
        
        # Extract all student enrollments achieving the max mark
        # Sort enrollments lexicographically/naturally if tie-breaking requires consistent ordering
        toppers = sorted([enrollment for mark, enrollment in entries if mark == max_mark])
        subject_toppers[subject_code] = toppers

    return sem_top_k, subject_toppers


def main():
    """Main execution block reading input and displaying semester & subject merit results."""
    try:
        # Read n, k, m
        header = sys.stdin.readline().strip()
        if not header:
            return
            
        n, k, m = map(int, header.split())
        
        raw_records = []
        for _ in range(n):
            raw_records.append(sys.stdin.readline().strip())

        # Process logic
        sem_top_k, subject_toppers = process_campus_merit(n, k, m, raw_records)

        # Output Semester-wise Top-K
        for sem, enrollments in sem_top_k.items():
            print(f"Semester {sem}: {' '.join(enrollments)}")

        # Output Subject-wise Toppers
        for idx in range(1, m + 1):
            sub_code = f"S{idx}"
            toppers = subject_toppers.get(sub_code, [])
            print(f"{sub_code}: {' '.join(toppers)}")

    except Exception as e:
        print(f"Input Processing Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    conn = sqlite3.connect('sample.db')
    cursor = conn.cursor()

    # Drop existing tables
    cursor.executescript('''
        DROP TABLE IF EXISTS Projects;
        DROP TABLE IF EXISTS Students;
        DROP TABLE IF EXISTS Teams;
        DROP TABLE IF EXISTS TimeEntries;
    ''')

    # Create tables with simple, clear structure
    cursor.executescript('''
        CREATE TABLE Projects (
            project_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            budget INTEGER NOT NULL
        );

        CREATE TABLE Teams (
            team_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE Students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            project_id INTEGER,
            grade FLOAT DEFAULT 0.0,
            enrollment_date DATE NOT NULL,
            FOREIGN KEY (project_id) REFERENCES Projects(project_id),
            FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        );

        CREATE TABLE TimeEntries (
            entry_id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL,
            hours INTEGER NOT NULL,
            task_date DATE NOT NULL,
            task_type TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        );
    ''')

    # Sample data for Projects
    projects = [
        (1, "Database System", "Computer Science", 50000),
        (2, "Mobile App", "Software Engineering", 75000),
        (3, "AI Research", "Data Science", 100000),
        (4, "Web Platform", "Information Technology", 60000)
    ]
    cursor.executemany('INSERT INTO Projects VALUES (?,?,?,?)', projects)

    # Sample data for Teams
    teams = [
        (1, "Alpha Team"),
        (2, "Beta Team"),
        (3, "Gamma Team"),
        (4, "Delta Team")
    ]
    cursor.executemany('INSERT INTO Teams VALUES (?,?)', teams)

    # Generate students with consistent team assignments
    students = []
    names = [
        "John Smith", "Emma Davis", "Michael Chen", "Sarah Wilson",
        "David Brown", "Lisa Anderson", "James Taylor", "Emily White",
        "Daniel Lee", "Sophie Clark", "Ryan Martinez", "Olivia Wang"
    ]
    
    for i, name in enumerate(names, 1):
        team_id = (i-1) // 3 + 1  # 3 students per team
        project_id = (i-1) // 3 + 1  # Each team works on one project
        grade = round(random.uniform(3.0, 4.0), 2)
        enrollment_date = datetime(2023, random.randint(1, 12), random.randint(1, 28)).date()
        students.append((i, name, team_id, project_id, grade, enrollment_date))
    
    cursor.executemany('INSERT INTO Students VALUES (?,?,?,?,?,?)', students)

    # Generate time entries
    time_entries = []
    task_types = ["Development", "Testing", "Documentation", "Meeting", "Research"]
    base_date = datetime(2024, 1, 1).date()
    
    for i in range(1, 51):
        student_id = random.randint(1, len(names))
        hours = random.randint(1, 8)
        days_offset = random.randint(0, 60)
        task_date = base_date + timedelta(days=days_offset)
        task_type = random.choice(task_types)
        time_entries.append((i, student_id, hours, task_date, task_type))

    cursor.executemany('INSERT INTO TimeEntries VALUES (?,?,?,?,?)', time_entries)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database created successfully with sample data!")
import sqlite3
import json
from datetime import datetime, timedelta
import random

def create_database():
    conn = sqlite3.connect('sample.db')
    cursor = conn.cursor()

    # Create project table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        company TEXT NOT NULL
    )
    ''')

    # Create student table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student (
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        team INTEGER NOT NULL,
        entry_count INTEGER DEFAULT 0,
        total_time FLOAT DEFAULT 0,
        team_rating FLOAT DEFAULT 0,
        project INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone_number TEXT,
        email TEXT NOT NULL,
        FOREIGN KEY (project) REFERENCES project(id)
    )
    ''')

    # Create time_entry table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS time_entry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author INTEGER NOT NULL,
        time_spent INTEGER NOT NULL,
        comments TEXT DEFAULT '{"Accomplished": "", "Roadblocks": "", "Plans": ""}',
        created DATETIME NOT NULL,
        updated DATETIME NOT NULL,
        FOREIGN KEY (author) REFERENCES student(sid)
    )
    ''')

    # Create faculty table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faculty (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        team INTEGER NOT NULL,
        project INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone_number TEXT,
        email TEXT NOT NULL,
        FOREIGN KEY (project) REFERENCES project(id)
    )
    ''')

    # Create review_prompt table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_prompt (
        pid INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        weight FLOAT DEFAULT 0
    )
    ''')

    # Create peer_review table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS peer_review (
        rid INTEGER PRIMARY KEY AUTOINCREMENT,
        author INTEGER NOT NULL,
        recipient INTEGER NOT NULL,
        prompt INTEGER NOT NULL,
        comments TEXT,
        created DATETIME NOT NULL,
        updated DATETIME,
        FOREIGN KEY (author) REFERENCES student(sid),
        FOREIGN KEY (recipient) REFERENCES student(sid),
        FOREIGN KEY (prompt) REFERENCES review_prompt(pid)
    )
    ''')

    # Insert sample data
    # Projects
    projects = [
        (1, "AI Chatbot", "Developing an AI-powered chatbot for customer service automation using NLP", "TechCorp"),
        (2, "Data Analytics Platform", "Building a comprehensive data analytics dashboard for business intelligence", "DataCo"),
        (3, "Mobile Fitness App", "Creating a fitness tracking mobile application with social features", "FitTech"),
        (4, "E-commerce Platform", "Developing a scalable e-commerce solution with ML recommendations", "ShopTech"),
        (5, "Healthcare Management System", "Building a patient management system with EMR integration", "MedTech"),
        (6, "Smart Home IoT Platform", "Creating an IoT platform for smart home device management", "IoTCorp"),
        (7, "Educational Learning Platform", "Developing an adaptive learning platform with AI tutoring", "EduTech"),
        (8, "Financial Analytics Tool", "Building a financial analysis and prediction platform", "FinCorp")
    ]
    cursor.executemany('INSERT OR REPLACE INTO project VALUES (?,?,?,?)', projects)

    # Students
    students = [
        (1, 1, 8, 45.5, 4.5, 1, "John Smith", "123-456-7890", "john.smith@email.com"),
        (2, 1, 6, 35.0, 4.2, 1, "Emma Johnson", "123-456-7891", "emma.j@email.com"),
        (3, 1, 7, 40.0, 4.8, 1, "Michael Brown", "123-456-7892", "michael.b@email.com"),
        (4, 2, 9, 50.0, 4.6, 2, "Sarah Davis", "123-456-7893", "sarah.d@email.com"),
        (5, 2, 5, 32.5, 4.3, 2, "David Wilson", "123-456-7894", "david.w@email.com"),
        (6, 2, 8, 42.0, 4.7, 2, "Lisa Anderson", "123-456-7895", "lisa.a@email.com"),
        (7, 3, 6, 38.0, 4.4, 3, "James Taylor", "123-456-7896", "james.t@email.com"),
        (8, 3, 7, 41.5, 4.5, 3, "Emily White", "123-456-7897", "emily.w@email.com"),
        (9, 3, 5, 30.0, 4.2, 3, "Daniel Lee", "123-456-7898", "daniel.l@email.com"),
        (10, 4, 8, 44.0, 4.6, 4, "Sophie Clark", "123-456-7899", "sophie.c@email.com"),
        (11, 4, 7, 39.0, 4.3, 4, "Ryan Martinez", "123-456-7900", "ryan.m@email.com"),
        (12, 4, 6, 36.5, 4.4, 4, "Olivia Wang", "123-456-7901", "olivia.w@email.com"),
        (13, 5, 9, 48.0, 4.8, 5, "William Chen", "123-456-7902", "william.c@email.com"),
        (14, 5, 7, 40.5, 4.5, 5, "Isabella Kim", "123-456-7903", "isabella.k@email.com"),
        (15, 5, 8, 43.0, 4.6, 5, "Lucas Garcia", "123-456-7904", "lucas.g@email.com"),
        (16, 6, 6, 35.5, 4.3, 6, "Ava Patel", "123-456-7905", "ava.p@email.com"),
        (17, 6, 7, 38.5, 4.4, 6, "Ethan Thompson", "123-456-7906", "ethan.t@email.com"),
        (18, 7, 8, 42.5, 4.7, 7, "Mia Rodriguez", "123-456-7907", "mia.r@email.com"),
        (19, 7, 6, 36.0, 4.2, 7, "Alexander Nguyen", "123-456-7908", "alex.n@email.com"),
        (20, 8, 7, 39.5, 4.5, 8, "Sophia Adams", "123-456-7909", "sophia.a@email.com")
    ]
    cursor.executemany('INSERT OR REPLACE INTO student VALUES (?,?,?,?,?,?,?,?,?)', students)

    # Faculty
    faculty = [
        (1, 1, 1, "Dr. Alice Thompson", "123-555-0101", "alice.t@university.edu"),
        (2, 2, 2, "Prof. Robert Chen", "123-555-0102", "robert.c@university.edu"),
        (3, 3, 3, "Dr. Maria Garcia", "123-555-0103", "maria.g@university.edu"),
        (4, 4, 4, "Prof. David Johnson", "123-555-0104", "david.j@university.edu"),
        (5, 5, 5, "Dr. Sarah Kim", "123-555-0105", "sarah.k@university.edu"),
        (6, 6, 6, "Prof. Michael Lee", "123-555-0106", "michael.l@university.edu"),
        (7, 7, 7, "Dr. Jennifer Wilson", "123-555-0107", "jennifer.w@university.edu"),
        (8, 8, 8, "Prof. Thomas Brown", "123-555-0108", "thomas.b@university.edu"),
        (9, 1, 1, "Dr. Emily Davis", "123-555-0109", "emily.d@university.edu"),
        (10, 2, 2, "Prof. James Martin", "123-555-0110", "james.m@university.edu"),
        (11, 3, 3, "Dr. Lisa Anderson", "123-555-0111", "lisa.a@university.edu"),
        (12, 4, 4, "Prof. William Taylor", "123-555-0112", "william.t@university.edu")
    ]
    cursor.executemany('INSERT OR REPLACE INTO faculty VALUES (?,?,?,?,?,?)', faculty)

    # Review Prompts
    prompts = [
        (1, "Technical Skills", "Rate the team member's technical contribution and coding abilities", 0.25),
        (2, "Communication", "Evaluate communication effectiveness within the team", 0.20),
        (3, "Initiative", "Assess level of initiative and proactiveness in project tasks", 0.15),
        (4, "Problem Solving", "Evaluate ability to solve complex technical problems", 0.20),
        (5, "Teamwork", "Rate collaboration and support of team members", 0.10),
        (6, "Project Management", "Assess organizational and planning capabilities", 0.10)
    ]
    cursor.executemany('INSERT OR REPLACE INTO review_prompt VALUES (?,?,?,?)', prompts)

    # Time Entries
    base_date = datetime.now() - timedelta(days=30)
    time_entries = []
    tasks = [
        "Implemented new feature", "Fixed bugs", "Code review", "Documentation",
        "Team meeting", "Client presentation", "Testing", "Database optimization",
        "UI/UX improvements", "API development"
    ]
    
    for i in range(1, 51):
        author = random.randint(1, 20)
        time_spent = random.randint(1, 8)
        task = random.choice(tasks)
        comments = json.dumps({
            "Accomplished": f"{task} #{i}",
            "Roadblocks": random.choice(["None", "Technical issues", "Waiting for review", "Dependencies"]),
            "Plans": f"Continue with {random.choice(['development', 'testing', 'documentation', 'optimization'])}"
        })
        created = base_date + timedelta(days=random.randint(1, 30))
        time_entries.append((i, author, time_spent, comments, created, created))

    cursor.executemany('INSERT OR REPLACE INTO time_entry VALUES (?,?,?,?,?,?)', time_entries)

    # Peer Reviews
    peer_reviews = []
    review_comments = [
        "Excellent technical skills and team collaboration",
        "Good communication but needs improvement in technical documentation",
        "Shows great initiative and problem-solving abilities",
        "Strong in project management and team coordination",
        "Effective contributor with good technical knowledge",
        "Demonstrates leadership and technical expertise",
        "Great team player with strong coding skills",
        "Excellent problem solver and communicator"
    ]
    
    for i in range(1, 41):
        author = random.randint(1, 20)
        recipient = random.randint(1, 20)
        while recipient == author:
            recipient = random.randint(1, 20)
        prompt = random.randint(1, 6)
        created = base_date + timedelta(days=random.randint(1, 30))
        updated = created + timedelta(days=random.randint(0, 5))
        peer_reviews.append((
            i, author, recipient, prompt,
            random.choice(review_comments),
            created,
            updated
        ))

    cursor.executemany('INSERT OR REPLACE INTO peer_review VALUES (?,?,?,?,?,?,?)', peer_reviews)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database created successfully with sample data!") 
import os
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "schemeai.db")

def init_db():
    # Ensure database directory exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating tables...")

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        state TEXT,
        district TEXT,
        occupation TEXT,
        income REAL,
        education TEXT,
        category TEXT,
        disability_status TEXT,
        bpl_status TEXT,
        employment_status TEXT,
        family_size INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Schemes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL, -- Central or State
        state TEXT NOT NULL, -- 'All' or a specific state
        min_age INTEGER DEFAULT 0,
        max_age INTEGER DEFAULT 120,
        gender_target TEXT DEFAULT 'All', -- Male, Female, All
        min_income REAL DEFAULT 0.0,
        max_income REAL DEFAULT 10000000.0,
        education_target TEXT DEFAULT 'All',
        occupation_target TEXT DEFAULT 'All',
        disability_required TEXT DEFAULT 'No', -- Yes or No
        bpl_required TEXT DEFAULT 'No', -- Yes or No
        benefits TEXT,
        required_documents TEXT,
        official_link TEXT,
        description TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Recommendations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        inputs TEXT NOT NULL, -- JSON string of profile parameters
        recommended_scheme_ids TEXT NOT NULL, -- comma-separated scheme IDs
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # EligibilityHistory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eligibility_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        scheme_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- Eligible, Partially Eligible, Not Eligible
        missing_criteria TEXT, -- JSON or comma-separated list of missing requirements
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
    )
    """)

    # Bookmarks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        scheme_id INTEGER NOT NULL,
        bookmarked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE,
        UNIQUE(user_id, scheme_id)
    )
    """)

    # Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        rating INTEGER NOT NULL,
        message TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Categories Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        icon TEXT
    )
    """)

    # Documents Guide Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        purpose TEXT,
        obtain_method TEXT,
        validity TEXT,
        image_url TEXT
    )
    """)

    # Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, -- NULL means global notification for all users
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0, -- 0 for False, 1 for True
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Admins Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Seeding Default Admin
    cursor.execute("SELECT COUNT(*) FROM admins WHERE email = 'admin@schemeai.com'")
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash("admin123")
        cursor.execute("INSERT INTO admins (name, email, password_hash) VALUES (?, ?, ?)",
                       ("Super Admin", "admin@schemeai.com", admin_pass))
        print("Default admin created (admin@schemeai.com / admin123)")

    # Seeding Categories
    categories = [
        ("Student", "Educational schemes, scholarships, and skill development aids.", "fa-graduation-cap"),
        ("Farmer", "Agricultural assistance, subsidies, tools, and crop insurance.", "fa-tractor"),
        ("Women", "Safety, financial support, girl child, and maternity aids.", "fa-female"),
        ("Senior Citizen", "Pensions, medical support, security, and elderly cares.", "fa-blind"),
        ("Business", "Startups, MSME finance, collateral-free loans, and grants.", "fa-briefcase"),
        ("Employment", "Wage guarantees, skill training, and job search aids.", "fa-user-tie"),
        ("Education", "Tuition reimbursements, school aids, and digital learning.", "fa-book-open"),
        ("Health", "Subsidized insurance, treatment support, and pharmacy discounts.", "fa-heartbeat"),
        ("Housing", "Affordable home loans, subsidies, and toilet constructions.", "fa-home"),
        ("Agriculture", "Farming, fisheries, organic methods, and soil test cards.", "fa-leaf"),
        ("Pension", "Old age, widow support, destitutes, and social security pensions.", "fa-hand-holding-usd"),
        ("Startup", "Innovation loans, incubation, and tax exemptions.", "fa-lightbulb"),
        ("Scholarship", "Post-matric, pre-matric, merit scholarships, and fellowships.", "fa-award"),
        ("Disability", "Aids, specialized pensions, and reservation concessions.", "fa-wheelchair")
    ]
    
    for cat_name, cat_desc, cat_icon in categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name, description, icon) VALUES (?, ?, ?)", 
                       (cat_name, cat_desc, cat_icon))

    # Seeding Documents
    documents = [
        ("Aadhaar Card", "Primary identity and address verification document.", "Apply online at UIDAI portal or visit Aadhaar Seva Kendra.", "Lifetime", "/static/images/documents/aadhaar_sample.jpg"),
        ("PAN Card", "Permanent Account Number for tax and financial audits.", "Apply online on NSDL or UTITSL portal.", "Lifetime", "/static/images/documents/pan_sample.jpg"),
        ("Income Certificate", "Proof of annual income of the household.", "Obtain from Tehsildar / Revenue Department or local CSC center.", "1 Year (Financial Year)", "/static/images/documents/income_sample.jpg"),
        ("Caste Certificate", "Verification of reservation category (SC/ST/OBC).", "Apply via SDM / Revenue Department or State Citizen Portal.", "Lifetime", "/static/images/documents/caste_sample.jpg"),
        ("Domicile Certificate", "Proof of residence in a specific state.", "Obtain from local Revenue Office (Tehsildar) or CSC.", "Lifetime / State specific", "/static/images/documents/domicile_sample.jpg"),
        ("Bank Passbook", "Verification of active account for direct benefit transfers (DBT).", "Issued by your local bank branch upon opening account.", "Lifetime (Keep updated)", "/static/images/documents/bank_sample.jpg"),
        ("Passport Photo", "Visual identity verification.", "Get clicked at any local studio or print online.", "Recent 6 months recommended", "/static/images/documents/photo_sample.jpg"),
        ("Birth Certificate", "Official proof of age and child details.", "Municipal Corporation, Gram Panchayat, or Registrar of Births.", "Lifetime", "/static/images/documents/birth_sample.jpg"),
        ("Disability Certificate", "Proof of physical, visual, or cognitive handicap.", "Issued by District Medical Board / Civil Hospital after assessment.", "Lifetime or Renew-based on disability degree", "/static/images/documents/disability_sample.jpg")
    ]

    for doc_name, doc_purp, doc_method, doc_val, doc_img in documents:
        cursor.execute("INSERT OR IGNORE INTO documents (name, purpose, obtain_method, validity, image_url) VALUES (?, ?, ?, ?, ?)", 
                       (doc_name, doc_purp, doc_method, doc_val, doc_img))

    # Import Schemes from CSV
    print("Seeding schemes from CSV...")
    if os.path.exists("dataset/schemes_sample.csv"):
        df = pd.read_csv("dataset/schemes_sample.csv")
        for idx, row in df.iterrows():
            cursor.execute("SELECT COUNT(*) FROM schemes WHERE name = ?", (row['name'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                INSERT INTO schemes (
                    id, name, department, category, type, state, min_age, max_age,
                    gender_target, min_income, max_income, education_target,
                    occupation_target, disability_required, bpl_required,
                    benefits, required_documents, official_link, description, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(row['id']),
                    row['name'],
                    row['department'],
                    row['category'],
                    row['type'],
                    row['state'],
                    int(row['min_age']),
                    int(row['max_age']),
                    row['gender_target'],
                    float(row['min_income']),
                    float(row['max_income']),
                    row['education_target'],
                    row['occupation_target'],
                    row['disability_required'],
                    row['bpl_required'],
                    row['benefits'],
                    row['required_documents'],
                    row['official_link'],
                    row['description'],
                    row['image_url']
                ))
        print("Schemes seeded successfully.")
    else:
        print("Warning: CSV file not found! Schemes seeding skipped.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()

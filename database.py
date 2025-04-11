import sqlite3

# Path to the database file
DATABASE_PATH = 'resumes.db'

# Function to create the database and table if they don't exist
def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create the resumes table with email as primary key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            phone TEXT,
            linkedin TEXT,
            github TEXT,
            degree TEXT,
            programming_languages TEXT,
            ml_tools TEXT,
            dev_tools TEXT,
            courseworks TEXT,
            soft_skills TEXT
        )
    ''')
    conn.commit()
    conn.close()
def insert_resume(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("DEBUG: Data to insert ->", data)  # 🛠️ Print extracted data before inserting

    # ✅ Use correct dictionary keys
    email = data.get('contact_info', {}).get('Email', '')
    phone = data.get('contact_info', {}).get('Mobile Number', '')
    linkedin = data.get('links', {}).get('Linkedin', '')
    github = data.get('links', {}).get('Github', '')

    # ✅ Extract skills properly
    programming_languages = ', '.join(data.get('skills', {}).get('programming_languages', []))
    ml_tools = ', '.join(data.get('skills', {}).get('ml_tools', []))
    dev_tools = ', '.join(data.get('skills', {}).get('dev_tools', []))
    courseworks = ', '.join(data.get('skills', {}).get('courseworks', []))
    soft_skills = ', '.join(data.get('skills', {}).get('soft_skills', []))

    cursor.execute('''
        INSERT INTO resumes (email, name, phone, linkedin, github, degree, 
                             programming_languages, ml_tools, dev_tools, courseworks, soft_skills)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET 
            name = excluded.name,
            phone = excluded.phone,
            linkedin = excluded.linkedin,
            github = excluded.github,
            degree = excluded.degree,
            programming_languages = excluded.programming_languages,
            ml_tools = excluded.ml_tools,
            dev_tools = excluded.dev_tools,
            courseworks = excluded.courseworks,
            soft_skills = excluded.soft_skills
    ''', (
        email, data.get('name', ''), phone, linkedin, github, data.get('degree', ''),
        programming_languages, ml_tools, dev_tools, courseworks, soft_skills
    ))

    conn.commit()
    print("DEBUG: Data inserted successfully ✅")  # 🛠️ Confirm data insertion
    conn.close()

    conn.close()


# Function to fetch all resumes
def fetch_all_resumes():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM resumes')
    rows = cursor.fetchall()

    conn.close()
    return rows

# Function to fetch a specific resume by email
def fetch_resume_by_email(email):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM resumes WHERE email = ?', (email,))
    row = cursor.fetchone()

    conn.close()
    return row
def fetch_resumes_from_db():
    conn = sqlite3.connect('resumes.db')  # Adjust DB connection as needed
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes")  # Fetch all resumes
    resumes = cursor.fetchall()  # Fetch as a list of tuples
    conn.close()

    # Convert list of tuples to list of dictionaries
    resume_list = []
    for row in resumes:
        resume_dict = {
            "id": row[0], "email": row[1], "name": row[2], "phone": row[3],
            "linkedin": row[4], "github": row[5], "degree": row[6],
            "programming_languages": row[7], "ml_tools": row[8],
            "dev_tools": row[9], "courseworks": row[10], "soft_skills": row[11]
        }
        resume_list.append(resume_dict)

    return resume_list  # ✅ Return list, not jsonify()


# Initialize the database when this script is run
if __name__ == '__main__':
    initialize_database()

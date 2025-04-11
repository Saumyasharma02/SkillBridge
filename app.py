from flask import Flask, render_template, request, jsonify
from upload import handle_upload
from database import fetch_all_resumes, fetch_resumes_from_db
from job_matching import match_resumes
import sqlite3

app = Flask(__name__)
app.secret_key = '123'  # Replace with a strong random key

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fetch')
def fetch_page():
    resumes = fetch_all_resumes()
    return render_template('fetch.html', resumes=resumes)

@app.route('/match')
def match_page():
    return render_template('match.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'POST':
        return handle_upload()  # Call function to process upload
    return render_template('upload.html')  # Show upload form


@app.route('/resumes', methods=['GET'])
def fetch_all_resumes():
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes")
    rows = cursor.fetchall()

    print("Fetched from DB:", rows)  # Debugging Line

    # Convert from array of arrays to array of objects
    resumes = [
        {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "phone": row[3],
            "linkedin": row[4],
            "github": row[5],
            "degree": row[6],
            "programming_languages": row[7],
            "ml_tools": row[8],
            "dev_tools": row[9],
            "courseworks": row[10],
            "soft_skills": row[11]
        }
        for row in rows
    ]

    conn.close()
    return jsonify(resumes)

@app.route('/resume', methods=['GET'])
def fetch_resume_by_email():
    email = request.args.get('email')

    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes WHERE email=?", (email,))
    row = cursor.fetchone()

    print("Fetched Resume:", row)  # DEBUGGING LINE

    if row:
        resume = {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "linkedin": row[4],
            "github": row[5],
            "degree": row[6],
            "programming_languages": row[7],
            "ml_tools": row[8],
            "dev_tools": row[9],
            "courseworks": row[10],
            "soft_skills": row[11]
        }
    else:
        return jsonify({"error": "No resume found"}), 404

    conn.close()
    return jsonify(resume)


@app.route('/match_resumes', methods=['POST'])
def match_resumes_route():
    job_description = request.json.get("job_description", "")
    resumes = fetch_resumes_from_db()

    print("Fetched resumes from DB:", resumes)
    print("Type of resumes:", type(resumes))

    if isinstance(resumes, list):
        sorted_resumes = match_resumes(job_description, resumes)
        return jsonify(sorted_resumes)
    else:
        return jsonify({"error": "Unexpected data format"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

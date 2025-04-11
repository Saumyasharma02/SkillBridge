import os
import logging
from werkzeug.utils import secure_filename
from resume import process_resume  # Ensure this function exists
from database import insert_resume  # Use the reusable function from database.py
from flask import request, flash, redirect, url_for, render_template, current_app

# Configure logging
logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_upload():
    if 'file' not in request.files:
        flash("No file part in the request.", "error")
        return redirect(url_for('upload_form'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected for uploading.", "error")
        return redirect(url_for('upload_form'))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Only PDF and DOCX are allowed.", "error")
        return redirect(url_for('upload_form'))

    # Save the file to the upload folder
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Extract data from the resume
    try:
        extracted_data = process_resume(filepath)
        if not extracted_data:
            flash("Failed to parse the resume. Please check the file format.", "error")
            return redirect(url_for('upload_form'))

        # ✅ Insert extracted data into the database
        with current_app.app_context():
            insert_resume(extracted_data)

        flash("Resume uploaded and processed successfully!", "success")
        return redirect(url_for('upload_form'))

    except Exception as e:
        logging.error(f"Error during resume parsing: {e}")
        flash("An unexpected error occurred while processing the resume.", "error")
        return redirect(url_for('upload_form'))
